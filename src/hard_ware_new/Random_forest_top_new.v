// Định nghĩa bit positions ở cấp độ toàn cục
// [node(9)] + [feature(2)] + [threshold(64)] + [left_child(9)] + [right_child(9)] + [prediction(2)] = 95 bits
`define NODE_ID_MSB 94
`define NODE_ID_LSB 86
`define FEATURE_MSB 85
`define FEATURE_LSB 84
`define THRESHOLD_MSB 83
`define THRESHOLD_LSB 20
`define LEFT_CHILD_MSB 19
`define LEFT_CHILD_LSB 11
`define RIGHT_CHILD_MSB 10
`define RIGHT_CHILD_LSB 2
`define PREDICTION_MSB 1
`define PREDICTION_LSB 0

module random_forest_top #(
    parameter NODE_WIDTH = 95,  // Changed from 120 to 95 bits
    parameter ADDR_WIDTH = 10,
    parameter ROM_DEPTH = 512,
    parameter TREE_COUNT = 21,  // Number of decision trees
    parameter PIPELINE_DEPTH = 10,  // Pipeline depth (also maximum tree depth)
    parameter ATTACK_THRESHOLD = 10,   // Ngưỡng số cây dự đoán tấn công (mặc định ngưỡng là 10 cây)
    parameter MIN_VOTES = 21     // Số phiếu tối thiểu cần thiết để đưa ra quyết định
)(
    input wire clk,
    input wire rst_n,

    // Input features from CAN bus
    input wire [63:0] arbitration_id,
    input wire [63:0] timestamp,
    input wire [63:0] data_field,
    
    input wire feature_valid, // Asserted when a new frame arrives
    output wire ready_for_next, // Indicates ready to receive next frame

    // Output
    output reg prediction_valid,
    output reg prediction_out,  // 0: normal, 1: attack
    output reg [4:0] frame_id_out  // ID of the frame being predicted
);

// Loop counters declared at module level
integer j;

// Count of frames currently in the pipeline
reg [4:0] current_frame_count;
reg [4:0] frame_id_in; // ID of incoming frame

// Use a streamlined voting approach
reg [TREE_COUNT-1:0] tree_votes; // One-hot votes from trees
reg [4:0] attack_votes; // Count of attack votes for current frame
reg [4:0] complete_votes; // Count of completed votes
reg [4:0] current_voting_frame; // Track which frame is voting

// Counter to keep prediction_valid high for multiple cycles
reg [3:0] prediction_valid_counter;

// Added: Frame processing flags
reg [1:0] frame_status [0:31]; // Status for each frame (0=not started, 1=in progress, 2=complete)
reg accepting_new_frames; // Flag to control when to accept new frames

// Thêm bộ đếm timeout cho trạng thái COLLECTING
reg [31:0] collecting_timeout_counter;

// Wires to connect instances of the pipelined tree
wire [TREE_COUNT-1:0] tree_predictions;
wire [TREE_COUNT-1:0] tree_prediction_valids;
wire [TREE_COUNT-1:0] tree_ready_for_next;
wire [4:0] tree_frame_id[0:TREE_COUNT-1]; // Frame ID being processed by each tree

// Modified to only allow new frames when we're ready
assign ready_for_next = (&tree_ready_for_next) && accepting_new_frames;

// Create 21 instances for each decision tree (with pipeline)
genvar i;
generate
    for (i = 0; i < TREE_COUNT; i = i + 1) begin : tree_instances
        pipelined_tree #(
            .NODE_WIDTH(NODE_WIDTH),
            .ADDR_WIDTH(ADDR_WIDTH),
            .ROM_DEPTH(ROM_DEPTH),
            .TREE_INDEX(i),  // Tree index to load correct weight file
            .PIPELINE_STAGES(PIPELINE_DEPTH)
        ) u_tree (
            .clk(clk),
            .rst_n(rst_n),
            .arbitration_id(arbitration_id),
            .timestamp(timestamp),
            .data_field(data_field),
            .feature_valid(feature_valid),
            .frame_id_in(frame_id_in),
            .ready_for_next(tree_ready_for_next[i]),
            .prediction_valid(tree_prediction_valids[i]),
            .prediction_out(tree_predictions[i]),
            .frame_id_out(tree_frame_id[i])
        );
    end
endgenerate

// Simplified FSM state definitions
localparam [1:0] IDLE = 2'b00;
localparam [1:0] COLLECTING = 2'b01;
localparam [1:0] VOTING = 2'b10;
localparam [1:0] WAIT_PREDICTION = 2'b11;

reg [1:0] state;

// Main state machine and voting logic
always @(posedge clk or negedge rst_n) begin
    // Khai báo biến local ở đầu khối procedural
    reg [4:0] adjusted_threshold;
    
    if (!rst_n) begin
        state <= IDLE;
        frame_id_in <= 0;
        current_frame_count <= 0;
        tree_votes <= 0;
        attack_votes <= 0;
        complete_votes <= 0;
        current_voting_frame <= 0;
        prediction_valid <= 0;
        prediction_valid_counter <= 0;
        prediction_out <= 0;
        frame_id_out <= 0;
        accepting_new_frames <= 1; // Start by accepting frames
        collecting_timeout_counter <= 0; // Khởi tạo bộ đếm timeout
        
        // Initialize frame status
        for (j = 0; j < 32; j = j + 1) 
            frame_status[j] <= 0;
    end else begin
        // Handle prediction_valid counter
        if (prediction_valid_counter > 0) begin
            prediction_valid_counter <= prediction_valid_counter - 1;
            prediction_valid <= 1; // Keep prediction_valid high
        end else if (prediction_valid) begin
            prediction_valid <= 0; // When counter reaches 0, lower prediction_valid
        end
        
        // Debug counter for vote monitoring
        if (state == COLLECTING || state == IDLE)
           $display("DEBUG_VOTES: Current frame=%0d, complete_votes=%0d/%0d, attack_votes=%0d at time %0t", 
                   current_voting_frame, complete_votes, TREE_COUNT, attack_votes, $time);
        
        case (state)
            IDLE: begin
                // Accept new frame if ready and frame is valid
                if (ready_for_next && feature_valid) begin
                    frame_id_in <= frame_id_in + 1;
                    frame_status[frame_id_in] <= 1; // Mark frame as in progress
                    state <= COLLECTING;
                    $display("MAIN: Accepting new frame %0d at time %0t", 
                           frame_id_in, $time);
                            
                    // Stop accepting new frames until we finish the current ones
                    accepting_new_frames <= 0;
                    $display("FLOW_CONTROL: Stopping new frames until voting completes");
                end
                
                // Check for new prediction results
                for (j = 0; j < TREE_COUNT; j = j + 1) begin
                    if (tree_prediction_valids[j]) begin
                        if (tree_frame_id[j] == current_voting_frame) begin
                            tree_votes[j] <= tree_predictions[j];
                            if (tree_predictions[j]) begin
                                attack_votes <= attack_votes + 1;
                                $display("VOTE_UPDATE[IDLE]: Frame %0d, Tree %0d votes ATTACK, attack_votes now %0d/%0d",
                                        current_voting_frame, j, attack_votes + 1, TREE_COUNT);
                            end else begin
                                $display("VOTE_UPDATE[IDLE]: Frame %0d, Tree %0d votes NORMAL, attack_votes still %0d/%0d",
                                        current_voting_frame, j, attack_votes, TREE_COUNT);
                            end
                            complete_votes <= complete_votes + 1;
                            $display("VOTE_COUNT[IDLE]: Frame %0d complete_votes now %0d/%0d",
                                    current_voting_frame, complete_votes + 1, TREE_COUNT);
                        end else begin
                            // Log mismatched frame IDs - important debug info
                            $display("FRAME_MISMATCH[IDLE]: Tree %0d voted for frame %0d but current voting frame is %0d",
                                    j, tree_frame_id[j], current_voting_frame);
                        end
                    end
                end
                
                // Check if we have all votes for current frame - SỬ DỤNG MIN_VOTES thay vì TREE_COUNT
                if (complete_votes >= MIN_VOTES) begin
                    state <= VOTING;
                    $display("VOTE_COMPLETE[IDLE]: Frame %0d has sufficient votes (%0d/%0d, min required: %0d), attack_votes=%0d, moving to VOTING at time %0t",
                            current_voting_frame, complete_votes, TREE_COUNT, MIN_VOTES, attack_votes, $time);
                end
            end
            
            COLLECTING: begin
                // Just collect tree outputs until we have them all
                for (j = 0; j < TREE_COUNT; j = j + 1) begin
                    if (tree_prediction_valids[j]) begin
                        if (tree_frame_id[j] == current_voting_frame) begin
                            tree_votes[j] <= tree_predictions[j];
                            if (tree_predictions[j]) begin
                                attack_votes <= attack_votes + 1;
                                $display("VOTE_UPDATE[COLLECT]: Frame %0d, Tree %0d votes ATTACK, attack_votes now %0d/%0d",
                                        current_voting_frame, j, attack_votes + 1, TREE_COUNT);
                            end else begin
                                $display("VOTE_UPDATE[COLLECT]: Frame %0d, Tree %0d votes NORMAL, attack_votes still %0d/%0d",
                                        current_voting_frame, j, attack_votes, TREE_COUNT);
                            end
                            complete_votes <= complete_votes + 1;
                            $display("VOTE_COUNT[COLLECT]: Frame %0d complete_votes now %0d/%0d",
                                    current_voting_frame, complete_votes + 1, TREE_COUNT);
                        end else begin
                            // Log mismatched frame IDs - important debug info
                            $display("FRAME_MISMATCH[COLLECT]: Tree %0d voted for frame %0d but current voting frame is %0d",
                                    j, tree_frame_id[j], current_voting_frame);
                        end
                    end
                end
                
                // If we got all votes for current frame, move to voting - SỬ DỤNG MIN_VOTES thay vì TREE_COUNT
                if (complete_votes >= MIN_VOTES) begin
                    state <= VOTING;
                    $display("VOTE_COMPLETE[COLLECT]: Frame %0d has sufficient votes (%0d/%0d, min required: %0d), attack_votes=%0d, moving to VOTING at time %0t",
                            current_voting_frame, complete_votes, TREE_COUNT, MIN_VOTES, attack_votes, $time);
                end
                
                // Thêm timeout cho trạng thái COLLECTING để tránh bị kẹt
                // Nếu sau 70000 chu kỳ mà vẫn chưa đủ phiếu, coi như đã đủ và tiến hành bỏ phiếu
                if (collecting_timeout_counter >= 70000) begin
                    $display("WARNING: Timeout in COLLECTING state for frame %0d, only got %0d/%0d votes. Proceeding to VOTING anyway.",
                            current_voting_frame, complete_votes, TREE_COUNT);
                    state <= VOTING;
                    collecting_timeout_counter <= 0;
                end else begin
                    collecting_timeout_counter <= collecting_timeout_counter + 1;
                    
                    // Thêm log để theo dõi timeout
                    if (collecting_timeout_counter % 1000 == 0) begin
                        $display("TIMEOUT_MONITOR: Frame %0d waiting for votes: %0d/%0d after %0d cycles",
                                current_voting_frame, complete_votes, TREE_COUNT, collecting_timeout_counter);
                        
                        // In chi tiết cây nào đã bỏ phiếu
                        $display("VOTE_DETAIL: Trees voted for frame %0d: ", current_voting_frame);
                        for (j = 0; j < TREE_COUNT; j = j + 1) begin
                            if (tree_prediction_valids[j] && tree_frame_id[j] == current_voting_frame) begin
                                $display("  - Tree %0d: %s", j, tree_predictions[j] ? "ATTACK" : "NORMAL");
                            end else begin
                                $display("  - Tree %0d: NOT_VOTED_YET", j);
                            end
                        end
                    end
                end
                
                // Accept new frames in COLLECTING only if we're allowed to
                if (ready_for_next && feature_valid && accepting_new_frames) begin
                    frame_id_in <= frame_id_in + 1;
                    frame_status[frame_id_in] <= 1; // Mark frame as in progress
                    $display("MAIN: Accepting new frame %0d while collecting at time %0t", 
                           frame_id_in + 1, $time);
                end
            end
            
            VOTING: begin
                // Reset timeout counter
                collecting_timeout_counter <= 0;
                
                // Tính toán ngưỡng tấn công dựa trên số phiếu thực tế
                // Nếu tỷ lệ phiếu tấn công >= tỷ lệ ngưỡng, thì kết quả là tấn công
                adjusted_threshold = (complete_votes * ATTACK_THRESHOLD) / TREE_COUNT;
                
                // Nghiêm ngặt so sánh số phiếu với ngưỡng
                // Không dùng biểu thức phức tạp, chỉ so sánh trực tiếp
                $display("VOTING_DECISION: Frame %0d, attack_votes=%0d/%0d, adjusted_threshold=%0d/%0d at time %0t", 
                        current_voting_frame, attack_votes, complete_votes, adjusted_threshold, complete_votes, $time);
                
                // Bắt buộc phải ghi chép phần này
                $display("EXPLICIT: attack_votes=%0d, adjusted_threshold=%0d, comparison=%0d", 
                        attack_votes, adjusted_threshold, (attack_votes >= adjusted_threshold ? 1 : 0));
                
                if (attack_votes >= adjusted_threshold) begin
                    // Xác định là TẤN CÔNG
                    prediction_out <= 1'b1;
                    $display("SET_ATTACK: Frame %0d is ATTACK (attack_votes=%0d >= adjusted_threshold=%0d)",
                            current_voting_frame, attack_votes, adjusted_threshold);
                end 
                else begin
                    // Xác định là BÌNH THƯỜNG
                    prediction_out <= 1'b0;
                    $display("SET_NORMAL: Frame %0d is NORMAL (attack_votes=%0d < adjusted_threshold=%0d)",
                            current_voting_frame, attack_votes, adjusted_threshold);
                end
                
                // Báo có kết quả dự đoán hợp lệ và giữ nó cao trong nhiều chu kỳ
                prediction_valid <= 1'b1;
                prediction_valid_counter <= 4'hF; // Hold prediction valid for 15 cycles
                frame_id_out <= current_voting_frame;
                
                // Mark this frame as complete
                frame_status[current_voting_frame] <= 2;
                
                // Mã gỡ lỗi
                $display("VOTING SUMMARY: Frame=%0d, Attack_votes=%0d/%0d, Threshold=%0d, Result=%b at time %0t", 
                        current_voting_frame, attack_votes, TREE_COUNT, adjusted_threshold, 
                        (attack_votes >= adjusted_threshold ? 1'b1 : 1'b0), $time);
                
                // Hiển thị chi tiết phiếu bầu từ mỗi cây
                $display("VOTE_DETAILS: Tree votes for frame %0d:", current_voting_frame);
                for (j = 0; j < TREE_COUNT; j = j + 1) begin
                    if (j < complete_votes) begin
                        $display("  - Tree %0d: %s", j, tree_votes[j] ? "ATTACK" : "NORMAL");
                    end else begin
                        $display("  - Tree %0d: NOT_VOTED", j);
                    end
                end
                
                // Wait to ensure prediction is captured before resetting
                state <= WAIT_PREDICTION;
            end
            
            WAIT_PREDICTION: begin
                // Stay in this state for one cycle to ensure prediction is captured
                // before resetting voting state for next frame
                
                // Thêm thông tin debug về frame vừa xử lý
                $display("FRAME_PROCESSED: Frame %0d completed with %0d/%0d votes, %0d attack votes",
                        current_voting_frame, complete_votes, TREE_COUNT, attack_votes);
                
                // Chuyển sang khung tiếp theo
                current_voting_frame <= current_voting_frame + 1;
                tree_votes <= 0;
                attack_votes <= 0;
                complete_votes <= 0;
                state <= IDLE;
                
                // Resume accepting frames
                accepting_new_frames <= 1;
                $display("FLOW_CONTROL: Resuming new frames for next frame %0d at time %0t", 
                        current_voting_frame + 1, $time);
                
                $display("PREDICTION_COMPLETE: Moving to next frame %0d at time %0t", 
                        current_voting_frame + 1, $time);
            end
            
            default: begin
                state <= IDLE;
            end
        endcase
    end
end

endmodule

// Module for each decision tree with pipeline support
module pipelined_tree #(
    parameter NODE_WIDTH = 95,  // Changed from 120 to 95 bits
    parameter ADDR_WIDTH = 10,
    parameter ROM_DEPTH = 512,
    parameter TREE_INDEX = 0,  // Tree index (0-20)
    parameter PIPELINE_STAGES = 10  // Maximum number of pipeline stages
)(
    input wire clk,
    input wire rst_n,

    // Input features from CAN bus
    input wire [63:0] arbitration_id,
    input wire [63:0] timestamp,
    input wire [63:0] data_field,
    
    input wire feature_valid, // Asserted when a new frame arrives
    input wire [4:0] frame_id_in, // ID of incoming frame
    
    output reg ready_for_next, // Indicates ready for next frame
    output reg prediction_valid, // Indicates valid prediction result
    output reg prediction_out,  // 0: normal, 1: attack
    output reg [4:0] frame_id_out // ID of processed frame
);

// Loop counter and flag declared at module level
integer pipe_index; // Changed from i to pipe_index to avoid conflict
reg found_valid_frame;

// ================== Pipeline Structures ======================
// Replace struct with individual arrays
reg [0:PIPELINE_STAGES-1] pipeline_valid;
reg [4:0] pipeline_frame_id [0:PIPELINE_STAGES-1];
reg [ADDR_WIDTH-1:0] pipeline_current_node [0:PIPELINE_STAGES-1];
reg [1:0] pipeline_prediction [0:PIPELINE_STAGES-1]; // Changed from 4 to 2 bits
reg [0:PIPELINE_STAGES-1] pipeline_is_done;

// ================== Internal ======================
wire [NODE_WIDTH-1:0] node_data;
reg [ADDR_WIDTH-1:0] read_addr; // Address being read
reg read_enable; // Add read enable signal

// Temporary signals for current node processing
reg [63:0] feature_value;
reg [63:0] temp_feature_value; // Moved declaration here
reg [1:0] feature_code; // Changed from 4 to 2 bits

// Cache the current node data to avoid re-reading
reg [NODE_WIDTH-1:0] current_node_data;

// Counter to keep prediction_valid high for multiple cycles
reg [3:0] prediction_valid_counter;

// Thêm bộ đếm độ sâu duyệt cây để tránh vòng lặp vô hạn
reg [4:0] traverse_depth;

// Thêm bộ đếm timeout cho trạng thái READ_NODE
reg [15:0] read_node_timeout;

// ================== Instantiate ROM ====================
tree_weight_rom #(
    .NODE_WIDTH(NODE_WIDTH),
    .ADDR_WIDTH(ADDR_WIDTH),
    .ROM_DEPTH(ROM_DEPTH),
    .TREE_INDEX(TREE_INDEX),
    .PIPELINE_STAGES(PIPELINE_STAGES)
) u_tree_weight_rom (
    .clk(clk),
    .addr(read_addr),
    .enable(read_enable), // Only read when enabled
    .node_data(node_data)
);

// Function to select feature (moved outside procedural block)
function [63:0] select_feature;
input [1:0] feature_code; // Changed from 4 to 2 bits
begin
    case (feature_code)
        2'b01: select_feature = arbitration_id;  // 01 = arbitration_id
        2'b00: select_feature = timestamp;       // 00 = timestamp
        2'b10: select_feature = data_field;      // 10 = data_field
        default: select_feature = 64'b0;
    endcase
end
endfunction

// NEW: Function to get root feature directly based on tree index
function [63:0] get_root_feature;
input integer tree_idx;
begin
    case (tree_idx)
        // timestamp: cây số 0,7,9,10,16,17
        0, 7, 9, 10, 16, 17: get_root_feature = timestamp;
        
        // data_field: 1,3,4,8,11,12,13,19
        1, 3, 4, 8, 11, 12, 13, 19: get_root_feature = data_field;
        
        // arbitration_id: 2,5,6,14,18,20
        2, 5, 6, 14, 18, 20: get_root_feature = arbitration_id;
        
        default: get_root_feature = arbitration_id; // Default to arbitration_id
    endcase
end
endfunction

// NEW: Function to get root feature code based on tree index
function [1:0] get_root_feature_code; // Changed from 4 to 2 bits
input integer tree_idx;
begin
    case (tree_idx)
        // timestamp (00): cây số 0,7,9,10,16,17
        0, 7, 9, 10, 16, 17: get_root_feature_code = 2'b00;
        
        // data_field (10): 1,3,4,8,11,12,13,19
        1, 3, 4, 8, 11, 12, 13, 19: get_root_feature_code = 2'b10;
        
        // arbitration_id (01): 2,5,6,14,18,20
        2, 5, 6, 14, 18, 20: get_root_feature_code = 2'b01;
        
        default: get_root_feature_code = 2'b01; // Default to arbitration_id
    endcase
end
endfunction

// States for decision tree traversal
localparam IDLE = 2'b00;
localparam READ_NODE = 2'b01; 
localparam PROCESS_NODE = 2'b10;
localparam OUTPUT_RESULT = 2'b11;

reg [1:0] tree_state;

// ================== Pipeline Control Logic =========================
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        // Reset all pipeline stages
        for (pipe_index = 0; pipe_index < PIPELINE_STAGES; pipe_index = pipe_index + 1) begin
            pipeline_valid[pipe_index] <= 0;
            pipeline_frame_id[pipe_index] <= 0;
            pipeline_current_node[pipe_index] <= 0;
            pipeline_prediction[pipe_index] <= 0;
            pipeline_is_done[pipe_index] <= 0;
        end
        
        read_addr <= 0;
        read_enable <= 0;
        ready_for_next <= 1;
        prediction_valid <= 0;
        prediction_valid_counter <= 0;
        prediction_out <= 0;
        frame_id_out <= 0;
        feature_code <= 0;
        found_valid_frame <= 0;
        tree_state <= IDLE;
        current_node_data <= 0;
        
        // Thêm bộ đếm độ sâu duyệt cây để tránh vòng lặp vô hạn
        traverse_depth <= 0;
        read_node_timeout <= 0;
    end else begin
        // Handle prediction_valid counter
        if (prediction_valid_counter > 0) begin
            prediction_valid_counter <= prediction_valid_counter - 1;
            // Keep prediction_valid high while counter is active
            prediction_valid <= 1;
        end else if (prediction_valid) begin
            // When counter reaches 0, lower prediction_valid
            prediction_valid <= 0;
        end
    
        // State machine for tree traversal
        case (tree_state)
            IDLE: begin
                read_enable <= 0;
                traverse_depth <= 0; // Reset độ sâu khi bắt đầu duyệt cây mới
                read_node_timeout <= 0; // Reset timeout counter
                
                if (!pipeline_valid[0] && feature_valid) begin
                    // Initialize first pipeline stage for new frame
                    pipeline_valid[0] <= 1;
                    pipeline_frame_id[0] <= frame_id_in;
                    pipeline_current_node[0] <= 0; // Start from root node
                    pipeline_prediction[0] <= 0;
                    pipeline_is_done[0] <= 0;
                    
                    // Set read address for root node and enable read
                    read_addr <= 0;
                    read_enable <= 1;
                    
                    // Signal frame has been accepted
                    ready_for_next <= 0;
                    
                    // Pre-calculate feature code for root node optimization
                    feature_code <= get_root_feature_code(TREE_INDEX);
                    feature_value <= get_root_feature(TREE_INDEX);
                    
                    tree_state <= READ_NODE;
                end
            end
            
            READ_NODE: begin
                // Latch the node data
                current_node_data <= node_data;
                read_enable <= 0;
                
                // Tăng bộ đếm timeout và kiểm tra
                read_node_timeout <= read_node_timeout + 1;
                if (read_node_timeout >= 3000) begin
                    // Nếu timeout, coi như node hiện tại là node lá
                    $display("WARNING: Tree %0d READ_NODE timeout at node %0d after %0d cycles, forcing leaf node",
                             TREE_INDEX, pipeline_current_node[0], read_node_timeout);
                    pipeline_prediction[0] <= 2'b00; // Giả sử dự đoán là "bình thường"
                    pipeline_is_done[0] <= 1;
                    tree_state <= OUTPUT_RESULT;
                    read_node_timeout <= 0;
                end
                // Kiểm tra độ sâu duyệt cây để tránh vòng lặp vô hạn
                else if (traverse_depth >= PIPELINE_STAGES) begin
                    // Nếu đã đạt đến độ sâu tối đa, coi như node hiện tại là node lá
                    $display("WARNING: Tree %0d reached maximum traverse depth at node %0d, forcing leaf node",
                             TREE_INDEX, pipeline_current_node[0]);
                    pipeline_prediction[0] <= 2'b00; // Giả sử dự đoán là "bình thường"
                    pipeline_is_done[0] <= 1;
                    tree_state <= OUTPUT_RESULT;
                end else begin
                    // Tăng độ sâu duyệt cây
                    traverse_depth <= traverse_depth + 1;
                    
                    // For non-root nodes, we need to extract feature code normally
                    if (pipeline_current_node[0] != 0) begin
                        tree_state <= PROCESS_NODE;
                        read_node_timeout <= 0; // Reset timeout counter
                    end else begin
                        // For root node, we already have feature_code and feature_value
                        // Skip the extraction step and go straight to comparison
                        
                        // Check if it's a leaf node based on feature code or prediction value
                        if (node_data[`FEATURE_MSB:`FEATURE_LSB] == 2'b11 || // Changed from 4'h3 to 2'b11 for leaf node indicator
                            node_data[`PREDICTION_MSB:`PREDICTION_LSB] != 2'b11) begin
                            // If leaf node, mark as completed
                            pipeline_prediction[0] <= node_data[`PREDICTION_MSB:`PREDICTION_LSB];
                            pipeline_is_done[0] <= 1;
                            tree_state <= OUTPUT_RESULT;
                        end else begin
                            // If internal node, prepare to read next node based on pre-determined feature
                            if (feature_value <= node_data[`THRESHOLD_MSB:`THRESHOLD_LSB]) begin
                                // Kiểm tra left_child có hợp lệ không
                                if (node_data[`LEFT_CHILD_MSB:`LEFT_CHILD_LSB] < ROM_DEPTH) begin
                                    pipeline_current_node[0] <= node_data[`LEFT_CHILD_MSB:`LEFT_CHILD_LSB];
                                    read_addr <= node_data[`LEFT_CHILD_MSB:`LEFT_CHILD_LSB];
                                    read_enable <= 1;
                                    tree_state <= READ_NODE;
                                    read_node_timeout <= 0; // Reset timeout counter
                                end else begin
                                    // Left_child không hợp lệ, coi như node lá
                                    $display("WARNING: Tree %0d, Node %0d has invalid left_child %0d, forcing leaf node",
                                             TREE_INDEX, pipeline_current_node[0], node_data[`LEFT_CHILD_MSB:`LEFT_CHILD_LSB]);
                                    pipeline_prediction[0] <= 2'b00;
                                    pipeline_is_done[0] <= 1;
                                    tree_state <= OUTPUT_RESULT;
                                end
                            end else begin
                                // Kiểm tra right_child có hợp lệ không
                                if (node_data[`RIGHT_CHILD_MSB:`RIGHT_CHILD_LSB] < ROM_DEPTH) begin
                                    pipeline_current_node[0] <= node_data[`RIGHT_CHILD_MSB:`RIGHT_CHILD_LSB];
                                    read_addr <= node_data[`RIGHT_CHILD_MSB:`RIGHT_CHILD_LSB];
                                    read_enable <= 1;
                                    tree_state <= READ_NODE;
                                    read_node_timeout <= 0; // Reset timeout counter
                                end else begin
                                    // Right_child không hợp lệ, coi như node lá
                                    $display("WARNING: Tree %0d, Node %0d has invalid right_child %0d, forcing leaf node",
                                             TREE_INDEX, pipeline_current_node[0], node_data[`RIGHT_CHILD_MSB:`RIGHT_CHILD_LSB]);
                                    pipeline_prediction[0] <= 2'b00;
                                    pipeline_is_done[0] <= 1;
                                    tree_state <= OUTPUT_RESULT;
                                end
                            end
                        end
                    end
                end
            end
            
            PROCESS_NODE: begin
                // Only for non-root nodes
                // Extract feature code from current node
                feature_code <= current_node_data[`FEATURE_MSB:`FEATURE_LSB];
                
                // Check if it's a leaf node based on feature code or prediction value
                if (current_node_data[`FEATURE_MSB:`FEATURE_LSB] == 2'b11 || // Changed from 4'h3 to 2'b11
                    current_node_data[`PREDICTION_MSB:`PREDICTION_LSB] != 2'b11) begin // Changed from 4'h3 to 2'b11
                    // If leaf node, mark as completed
                    pipeline_prediction[0] <= current_node_data[`PREDICTION_MSB:`PREDICTION_LSB];
                    pipeline_is_done[0] <= 1;
                    tree_state <= OUTPUT_RESULT;
                end else begin
                    // Get feature value for comparison (only for non-leaf nodes)
                    temp_feature_value = select_feature(current_node_data[`FEATURE_MSB:`FEATURE_LSB]);
                    feature_value <= temp_feature_value;
                    
                    // If internal node, prepare to read next node
                    if (temp_feature_value <= current_node_data[`THRESHOLD_MSB:`THRESHOLD_LSB]) begin
                        // Kiểm tra left_child có hợp lệ không
                        if (current_node_data[`LEFT_CHILD_MSB:`LEFT_CHILD_LSB] < ROM_DEPTH) begin
                            pipeline_current_node[0] <= current_node_data[`LEFT_CHILD_MSB:`LEFT_CHILD_LSB];
                            read_addr <= current_node_data[`LEFT_CHILD_MSB:`LEFT_CHILD_LSB];
                            read_enable <= 1;
                            tree_state <= READ_NODE;
                        end else begin
                            // Left_child không hợp lệ, coi như node lá
                            $display("WARNING: Tree %0d, Node %0d has invalid left_child %0d, forcing leaf node",
                                     TREE_INDEX, pipeline_current_node[0], current_node_data[`LEFT_CHILD_MSB:`LEFT_CHILD_LSB]);
                            pipeline_prediction[0] <= 2'b00;
                            pipeline_is_done[0] <= 1;
                            tree_state <= OUTPUT_RESULT;
                        end
                    end else begin
                        // Kiểm tra right_child có hợp lệ không
                        if (current_node_data[`RIGHT_CHILD_MSB:`RIGHT_CHILD_LSB] < ROM_DEPTH) begin
                            pipeline_current_node[0] <= current_node_data[`RIGHT_CHILD_MSB:`RIGHT_CHILD_LSB];
                            read_addr <= current_node_data[`RIGHT_CHILD_MSB:`RIGHT_CHILD_LSB];
                            read_enable <= 1;
                            tree_state <= READ_NODE;
                        end else begin
                            // Right_child không hợp lệ, coi như node lá
                            $display("WARNING: Tree %0d, Node %0d has invalid right_child %0d, forcing leaf node",
                                     TREE_INDEX, pipeline_current_node[0], current_node_data[`RIGHT_CHILD_MSB:`RIGHT_CHILD_LSB]);
                            pipeline_prediction[0] <= 2'b00;
                            pipeline_is_done[0] <= 1;
                            tree_state <= OUTPUT_RESULT;
                        end
                    end
                end
            end
            
            OUTPUT_RESULT: begin
                // Ready to accept next frame
                ready_for_next <= 1;
                
                // Output prediction and keep it valid for multiple cycles
                prediction_valid <= 1;
                prediction_valid_counter <= 4'hF; // Hold prediction valid for 15 cycles
                prediction_out <= pipeline_prediction[0][0]; // Bit 0 of prediction
                frame_id_out <= pipeline_frame_id[0];
                
                // Debug info
                $display("TREE %0d OUTPUTTING PREDICTION: Frame=%0d, Result=%b at time %0t", 
                         TREE_INDEX, pipeline_frame_id[0], 
                         pipeline_prediction[0][0], $time);
                
                // Clear the pipeline stage
                pipeline_valid[0] <= 0;
                tree_state <= IDLE;
            end
        endcase
    end
end

endmodule

// ROM module with tree index
module tree_weight_rom #(
    parameter NODE_WIDTH = 95, // Changed from 120 to 95 bits
    parameter ADDR_WIDTH = 10,
    parameter ROM_DEPTH = 512,
    parameter TREE_INDEX = 0,
    parameter PIPELINE_STAGES = 15 // Đổi từ PIPELINE_DEPTH thành PIPELINE_STAGES
)(
    input wire clk,
    input wire [ADDR_WIDTH-1:0] addr,
    input wire enable,  // Add enable signal
    output reg [NODE_WIDTH-1:0] node_data
);

// ROM memory containing node weights - limit depth based on the actual nodes needed
reg [NODE_WIDTH-1:0] rom [0:get_tree_depth(TREE_INDEX)-1];
// Variable declarations
integer rom_index; // Changed from i to rom_index to avoid conflict
integer file;
integer status;
reg [8*200:1] line;
reg [NODE_WIDTH-1:0] data;

// Function to get filename based on tree index
function [255:0] get_tree_file;
input integer index;
reg [255:0] file_name;
begin
    case (index)
        0: get_tree_file = "./tree_0_v.mif";
        1: get_tree_file = "./tree_1_v.mif";
        2: get_tree_file = "./tree_2_v.mif";
        3: get_tree_file = "./tree_3_v.mif";
        4: get_tree_file = "./tree_4_v.mif";
        5: get_tree_file = "./tree_5_v.mif";
        6: get_tree_file = "./tree_6_v.mif";
        7: get_tree_file = "./tree_7_v.mif";
        8: get_tree_file = "./tree_8_v.mif";
        9: get_tree_file = "./tree_9_v.mif";
        10: get_tree_file = "./tree_10_v.mif";
        11: get_tree_file = "./tree_11_v.mif";
        12: get_tree_file = "./tree_12_v.mif";
        13: get_tree_file = "./tree_13_v.mif";
        14: get_tree_file = "./tree_14_v.mif";
        15: get_tree_file = "./tree_15_v.mif";
        16: get_tree_file = "./tree_16_v.mif";
        17: get_tree_file = "./tree_17_v.mif";
        18: get_tree_file = "./tree_18_v.mif";
        19: get_tree_file = "./tree_19_v.mif";
        20: get_tree_file = "./tree_20_v.mif";
        default: get_tree_file = "./tree_0_v.mif";
    endcase
end
endfunction

// Get accurate node count for each tree
function integer get_tree_depth;
input integer index;
begin
    case (index)
        0: get_tree_depth = 223;  // Cập nhật đúng số node
        1: get_tree_depth = 373;  // Cập nhật đúng số node
        2: get_tree_depth = 247;  // Cập nhật đúng số node
        3: get_tree_depth = 301;  // Cập nhật đúng số node
        4: get_tree_depth = 295;  // Cập nhật đúng số node
        5: get_tree_depth = 223;  // Cập nhật đúng số node
        6: get_tree_depth = 245;  // Cập nhật đúng số node
        7: get_tree_depth = 213;  // Cập nhật đúng số node
        8: get_tree_depth = 287;  // Cập nhật đúng số node
        9: get_tree_depth = 253;  // Cập nhật đúng số node
        10: get_tree_depth = 321; // Cập nhật đúng số node
        11: get_tree_depth = 263; // Cập nhật đúng số node
        12: get_tree_depth = 319; // Cập nhật đúng số node
        13: get_tree_depth = 303; // Cập nhật đúng số node
        14: get_tree_depth = 215; // Cập nhật đúng số node
        15: get_tree_depth = 231; // Cập nhật đúng số node
        16: get_tree_depth = 355; // Cập nhật đúng số node
        17: get_tree_depth = 245; // Cập nhật đúng số node
        18: get_tree_depth = 227; // Cập nhật đúng số node
        19: get_tree_depth = 377; // Cập nhật đúng số node
        20: get_tree_depth = 259; // Cập nhật đúng số node
        default: get_tree_depth = 250;
    endcase
end
endfunction

// Cached ROM data to speed up simulation
reg [NODE_WIDTH-1:0] cached_data;
reg [ADDR_WIDTH-1:0] cached_addr;
reg cache_valid;

initial begin
    // Initialize ROM with zeros
    for (rom_index = 0; rom_index < get_tree_depth(TREE_INDEX); rom_index = rom_index + 1) begin
        rom[rom_index] = {NODE_WIDTH{1'b0}};
    end
    
    // Try different file paths
    $display("Loading tree weight file for tree %0d", TREE_INDEX);
    
    // Try with hard_ware_new prefix
    file = $fopen(get_tree_file(TREE_INDEX), "r");
    
    // If that fails, try without the prefix
    if (!file) begin
        file = $fopen(get_tree_file(TREE_INDEX), "r");
        if (!file) begin
            // Try with just the base filename
            case (TREE_INDEX)
                0: file = $fopen("tree_0_v.mif", "r");
                1: file = $fopen("tree_1_v.mif", "r");
                2: file = $fopen("tree_2_v.mif", "r");
                3: file = $fopen("tree_3_v.mif", "r");
                4: file = $fopen("tree_4_v.mif", "r");
                5: file = $fopen("tree_5_v.mif", "r");
                6: file = $fopen("tree_6_v.mif", "r");
                7: file = $fopen("tree_7_v.mif", "r");
                8: file = $fopen("tree_8_v.mif", "r");
                9: file = $fopen("tree_9_v.mif", "r");
                10: file = $fopen("tree_10_v.mif", "r");
                11: file = $fopen("tree_11_v.mif", "r");
                12: file = $fopen("tree_12_v.mif", "r");
                13: file = $fopen("tree_13_v.mif", "r");
                14: file = $fopen("tree_14_v.mif", "r");
                15: file = $fopen("tree_15_v.mif", "r");
                16: file = $fopen("tree_16_v.mif", "r");
                17: file = $fopen("tree_17_v.mif", "r");
                18: file = $fopen("tree_18_v.mif", "r");
                19: file = $fopen("tree_19_v.mif", "r");
                20: file = $fopen("tree_20_v.mif", "r");
            endcase
        end
    end
    
    if (file) begin
        $display("File opened successfully for tree %0d", TREE_INDEX);
        rom_index = 0;
        while (!$feof(file) && rom_index < get_tree_depth(TREE_INDEX)) begin
            status = $fgets(line, file);
            if (status != 0) begin
                // Skip if line contains "END;" keyword - simplified check
                // Removed problematic string comparison
                
                // Debug raw line for first few nodes
                if (rom_index < 3) begin
                    $display("Tree %0d, Reading line %0d: %s", TREE_INDEX, rom_index, line);
                end
                
                // Try reading as binary first
                data = 0;
                status = $sscanf(line, "%b", data);
                
                // If binary read fails, try hex format
                if (status <= 0) begin
                    status = $sscanf(line, "%h", data);
                end
                
                if (status > 0) begin
                    // Kiểm tra tính hợp lệ của node
                    // Trích xuất left_child và right_child
                    reg [8:0] left_child;
                    reg [8:0] right_child;
                    
                    left_child = data[`LEFT_CHILD_MSB:`LEFT_CHILD_LSB];
                    right_child = data[`RIGHT_CHILD_MSB:`RIGHT_CHILD_LSB];
                    
                    // Kiểm tra xem left_child và right_child có vượt quá ROM_DEPTH không
                    if (left_child >= ROM_DEPTH || right_child >= ROM_DEPTH) begin
                        $display("WARNING: Tree %0d, Node %0d has invalid child pointers: left=%0d, right=%0d",
                                 TREE_INDEX, rom_index, left_child, right_child);
                        
                        // Sửa lại các giá trị không hợp lệ
                        if (left_child >= ROM_DEPTH) begin
                            // Đặt left_child thành node lá (giá trị dự đoán 0)
                            data[`LEFT_CHILD_MSB:`LEFT_CHILD_LSB] = 0;
                            data[`FEATURE_MSB:`FEATURE_LSB] = 2'b11; // Đánh dấu là node lá
                        end
                        
                        if (right_child >= ROM_DEPTH) begin
                            // Đặt right_child thành node lá (giá trị dự đoán 0)
                            data[`RIGHT_CHILD_MSB:`RIGHT_CHILD_LSB] = 0;
                            data[`FEATURE_MSB:`FEATURE_LSB] = 2'b11; // Đánh dấu là node lá
                        end
                    end
                    
                    rom[rom_index] = data;
                    
                    // Debug node data for first few nodes
                    if (rom_index < 3) begin
                        $display("Tree %0d, Node %0d loaded: %h", TREE_INDEX, rom_index, data);
                        $display("  - feature: %b, left_child: %0d, right_child: %0d, prediction: %b",
                                 data[`FEATURE_MSB:`FEATURE_LSB],
                                 data[`LEFT_CHILD_MSB:`LEFT_CHILD_LSB],
                                 data[`RIGHT_CHILD_MSB:`RIGHT_CHILD_LSB],
                                 data[`PREDICTION_MSB:`PREDICTION_LSB]);
                    end
                    
                    rom_index = rom_index + 1;
                end
            end
        end
        $fclose(file);
        $display("Loaded %0d nodes for tree %0d", rom_index, TREE_INDEX);
    end else begin
        $display("ERROR: Could not open file for tree %0d", TREE_INDEX);
    end
    
    // Initialize cache
    cached_data = {NODE_WIDTH{1'b0}};
    cached_addr = {ADDR_WIDTH{1'b0}};
    cache_valid = 0;
end

always @(posedge clk) begin
    // Only read when enabled to save simulation time
    if (enable) begin
        // Check if the address is already cached
        if (cache_valid && cached_addr == addr) begin
            node_data <= cached_data;
        end else if (addr < get_tree_depth(TREE_INDEX)) begin
            cached_data <= rom[addr];
            cached_addr <= addr;
            cache_valid <= 1;
            node_data <= rom[addr];
        end else begin
            node_data <= {NODE_WIDTH{1'b0}};
            cache_valid <= 0;
        end
    end
end

endmodule