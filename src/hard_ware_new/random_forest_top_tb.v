`timescale 1ns/1ps

module random_forest_top_tb;
    // Parameters
    parameter NODE_WIDTH = 95;
    parameter ADDR_WIDTH = 10;
    parameter ROM_DEPTH = 512;
    parameter TREE_COUNT = 21;
    parameter PIPELINE_DEPTH = 20;
    parameter ATTACK_THRESHOLD = 10;
    parameter CLOCK_PERIOD = 20; // 20ns clock period (50MHz)
    
    // Signals for DUT
    reg clk;
    reg rst_n;
    reg [63:0] arbitration_id;
    reg [63:0] timestamp;
    reg [63:0] data_field;
    reg feature_valid;
    wire ready_for_next;
    wire prediction_valid;
    wire prediction_out;
    wire [4:0] frame_id_out;
    
    // Variables for testbench
    integer i;
    integer num_frames = 3; // Number of frames in CSV file
    integer wait_cycles;
    integer num_predictions = 0;
    integer num_attacks = 0;
    integer log_file;
    reg [1:0] frame_results [03]; // Store results: 0=not processed, 1=normal, 2=attack
    
    // Debug counters
    integer debug_counter = 0;
    integer debug_interval = 20000; // Print debug info every 20,000 cycles
    
    // Arrays to store data from CSV
    reg [63:0] test_timestamp [0:3];
    reg [63:0] test_arbitration_id [0:3];
    reg [63:0] test_data_field [0:3];
    
    // Instantiate DUT
    random_forest_top #(
        .NODE_WIDTH(NODE_WIDTH),
        .ADDR_WIDTH(ADDR_WIDTH),
        .ROM_DEPTH(ROM_DEPTH),
        .TREE_COUNT(TREE_COUNT),
        .PIPELINE_DEPTH(PIPELINE_DEPTH),
        .ATTACK_THRESHOLD(ATTACK_THRESHOLD)
    ) dut (
        .clk(clk),
        .rst_n(rst_n),
        .arbitration_id(arbitration_id),
        .timestamp(timestamp),
        .data_field(data_field),
        .feature_valid(feature_valid),
        .ready_for_next(ready_for_next),
        .prediction_valid(prediction_valid),
        .prediction_out(prediction_out),
        .frame_id_out(frame_id_out)
    );
    
    // Generate clock
    always #(CLOCK_PERIOD/2) clk = ~clk;
    
    // Debug monitor - print status periodically
    always @(posedge clk) begin
        debug_counter <= debug_counter + 1;
        
        if (debug_counter % debug_interval == 0) begin
            $display("DEBUG: Time %0t, Cycle %0d - State=%0d, Current voting frame=%0d, Complete votes=%0d/%0d", 
                     $time, debug_counter, dut.state, dut.current_voting_frame, dut.complete_votes, TREE_COUNT);
            $fdisplay(log_file, "DEBUG: Time %0t, Cycle %0d - State=%0d, Current voting frame=%0d, Complete votes=%0d/%0d", 
                     $time, debug_counter, dut.state, dut.current_voting_frame, dut.complete_votes, TREE_COUNT);
            
            // Check tree ready signals
            $display("DEBUG: ready_for_next=%b, accepting_new_frames=%b", ready_for_next, dut.accepting_new_frames);
            $fdisplay(log_file, "DEBUG: ready_for_next=%b, accepting_new_frames=%b", ready_for_next, dut.accepting_new_frames);
            
            // Check timeout counter
            $display("DEBUG: collecting_timeout_counter=%0d", dut.collecting_timeout_counter);
            $fdisplay(log_file, "DEBUG: collecting_timeout_counter=%0d", dut.collecting_timeout_counter);
            
            // Check tree ready signals
            $write("DEBUG: Tree ready signals: ");
            $fwrite(log_file, "DEBUG: Tree ready signals: ");
            for (i = 0; i < TREE_COUNT; i = i + 1) begin
                $write("%b", dut.tree_ready_for_next[i]);
                $fwrite(log_file, "%b", dut.tree_ready_for_next[i]);
            end
            $display("");
            $fdisplay(log_file, "");
            
            // Check tree prediction valid signals
            $write("DEBUG: Tree prediction valid signals: ");
            $fwrite(log_file, "DEBUG: Tree prediction valid signals: ");
            for (i = 0; i < TREE_COUNT; i = i + 1) begin
                $write("%b", dut.tree_prediction_valids[i]);
                $fwrite(log_file, "%b", dut.tree_prediction_valids[i]);
            end
            $display("");
            $fdisplay(log_file, "");
            
            // Check first tree state
            $display("DEBUG: First tree state: %0d", dut.tree_instances[0].u_tree.tree_state);
            $fdisplay(log_file, "DEBUG: First tree state: %0d", dut.tree_instances[0].u_tree.tree_state);
            
            // Add more detailed debugging for the first tree
            if (debug_counter % (debug_interval * 10) == 0) begin
                debug_tree_state(0);
                
                // Check if ROM data is being read correctly
                $display("DEBUG: Tree 0 - Current node data: %h", dut.tree_instances[0].u_tree.node_data);
                $fdisplay(log_file, "DEBUG: Tree 0 - Current node data: %h", dut.tree_instances[0].u_tree.node_data);
                
                // Check feature extraction
                $display("DEBUG: Tree 0 - Feature value: %h", dut.tree_instances[0].u_tree.feature_value);
                $fdisplay(log_file, "DEBUG: Tree 0 - Feature value: %h", dut.tree_instances[0].u_tree.feature_value);
                
                // Check ROM instance - remove reference to rom_enable
                $display("DEBUG: Tree 0 - Read address: %h", dut.tree_instances[0].u_tree.read_addr);
                $fdisplay(log_file, "DEBUG: Tree 0 - Read address: %h", dut.tree_instances[0].u_tree.read_addr);
                
                // Check traverse depth
                $display("DEBUG: Tree 0 - Traverse depth: %0d", dut.tree_instances[0].u_tree.traverse_depth);
                $fdisplay(log_file, "DEBUG: Tree 0 - Traverse depth: %0d", dut.tree_instances[0].u_tree.traverse_depth);
            end
        end
    end
    
    // Initialize test data from CSV
    // We use binary format to match exactly with the binary_64bit_output_v2.csv file
    initial begin
        // Initialize data from binary_64bit_output_v2.csv
        // Skip header line (line 1), start from line 2
        
        // Frame 0
        test_timestamp[0] = 64'b0000000000000000000000000000000001100011101100001100110111001011;
        test_arbitration_id[0] = 64'b0000000000000000000000000000000000000000000000000000001111101001;
        test_data_field[0] = 64'b0001001100111101000111001101110100010011000101000001100100001011;
        
        // Frame 1
        test_timestamp[1] = 64'b0100000111011000111011000011001111000010001111101011010111011100;
        test_arbitration_id[1] = 64'b0000000000000000000000000000000000000000000000000000000110000100;
        test_data_field[1] = 64'b0000000000000000000000000000001100000000000000000000000000000000;
        
        // Frame 2
        test_timestamp[2] = 64'b0100000111011000111011000011001101011010011001100111110100010100;
        test_arbitration_id[2] = 64'b0000000000000000000000000000000000000000000000000000000010101010;
        test_data_field[2] = 64'b0010111100000100001011011001000000000010010100100110111100000000;
        
        // Frame 3
        test_timestamp[3] = 64'b0100000111011000111011000011001101001010100101101101001000101101;
        test_arbitration_id[3] = 64'b0000000000000000000000000000000000000000000000000000001001011111;
        test_data_field[3] = 64'b0000000000000000110011111100000111001101001010101011010000010111;
        
        // // Frame 4
        // test_timestamp[4] = 64'b;
        // test_arbitration_id[4] = 64'b;
        // test_data_field[4] = 64'b;
        
        // // Frame 5
        // test_timestamp[5] = 64'b;
        // test_arbitration_id[5] = 64'b;
        // test_data_field[5] = 64'b;
        
        // // Frame 6
        // test_timestamp[6] = 64'b;
        // test_arbitration_id[6] = 64'b;
        // test_data_field[6] = 64'b;
        
        // // Frame 7
        // test_timestamp[7] = 64'b;
        // test_arbitration_id[7] = 64'b;
        // test_data_field[7] = 64'b;
        
        // // Frame 8
        // test_timestamp[8] = 64'b;
        // test_arbitration_id[8] = 64'b;
        // test_data_field[8] = 64'b;
        
        // // Frame 9
        // test_timestamp[9] = 64'b;
        // test_arbitration_id[9] = 64'b;
        // test_data_field[9] = 64'b;
        
        // Initialize frame results
        for (i = 0; i < num_frames; i = i + 1) begin
            frame_results[i] = 0; // Not processed yet
        end
    end
    
    // Task to send a frame
    task send_frame;
        input integer frame_idx;
        begin
            // Wait until DUT is ready to receive new frame
            wait(ready_for_next);
            @(posedge clk);
            
            // Set frame data
            timestamp = test_timestamp[frame_idx];
            arbitration_id = test_arbitration_id[frame_idx];
            data_field = test_data_field[frame_idx];
            feature_valid = 1;
            
            // Hold data for one clock cycle
            @(posedge clk);
            feature_valid = 0;
            
            $display("Time %0t: Sent frame %0d, timestamp=%h, arbitration_id=%h, data_field=%h", 
                     $time, frame_idx, timestamp, arbitration_id, data_field);
            $fdisplay(log_file, "Time %0t: Sent frame %0d, timestamp=%h, arbitration_id=%h, data_field=%h", 
                     $time, frame_idx, timestamp, arbitration_id, data_field);
        end
    endtask
    
    // Monitor prediction results
    always @(posedge clk) begin
        if (prediction_valid) begin
            num_predictions = num_predictions + 1;
            
            // Store the result for this frame
            if (frame_id_out < num_frames) begin
                frame_results[frame_id_out] = prediction_out ? 2 : 1; // 2=attack, 1=normal
            end
            
            if (prediction_out)
                num_attacks = num_attacks + 1;
                
            $display("Time %0t: Prediction for frame %0d: %s", 
                     $time, frame_id_out, prediction_out ? "ATTACK" : "NORMAL");
            $fdisplay(log_file, "Time %0t: Prediction for frame %0d: %s", 
                     $time, frame_id_out, prediction_out ? "ATTACK" : "NORMAL");
        end
    end
    
    // Test procedure
    initial begin
        // Open log file
        log_file = $fopen("random_forest_results.log", "w");
        if (!log_file) begin
            $display("Error: Could not open log file");
            $finish;
        end
        
        // Initialize signals
        clk = 0;
        rst_n = 0;
        feature_valid = 0;
        arbitration_id = 0;
        timestamp = 0;
        data_field = 0;
        
        // Reset system
        #(CLOCK_PERIOD*5);
        rst_n = 1;
        #(CLOCK_PERIOD*5);
        
        $display("Starting test with %0d frames", num_frames);
        $fdisplay(log_file, "Starting test with %0d frames", num_frames);
        
        // Send all frames with minimal delay between them
        for (i = 0; i < num_frames; i = i + 1) begin
            send_frame(i);
            
            // Wait just a few cycles between frames
            repeat(20) @(posedge clk);
        end
        
        // Wait until all predictions are completed
        // Wait enough time for pipeline to complete - increased significantly
        repeat(300000) @(posedge clk);
        
        // Report results
        $display("\n--- Test Summary ---");
        $display("Total frames sent: %0d", num_frames);
        $display("Total predictions received: %0d", num_predictions);
        $display("Normal frames: %0d", num_predictions - num_attacks);
        $display("Attack frames: %0d", num_attacks);
        
        // Detailed results for each frame
        $display("\n--- Detailed Frame Results ---");
        for (i = 0; i < num_frames; i = i + 1) begin
            case (frame_results[i])
                0: $display("Frame %0d: NOT PROCESSED", i);
                1: $display("Frame %0d: NORMAL", i);
                2: $display("Frame %0d: ATTACK", i);
            endcase
        end
        $display("-------------------\n");
        
        // Write results to log file
        $fdisplay(log_file, "\n--- Test Summary ---");
        $fdisplay(log_file, "Total frames sent: %0d", num_frames);
        $fdisplay(log_file, "Total predictions received: %0d", num_predictions);
        $fdisplay(log_file, "Normal frames: %0d", num_predictions - num_attacks);
        $fdisplay(log_file, "Attack frames: %0d", num_attacks);
        
        // Detailed results for each frame in log
        $fdisplay(log_file, "\n--- Detailed Frame Results ---");
        for (i = 0; i < num_frames; i = i + 1) begin
            case (frame_results[i])
                0: $fdisplay(log_file, "Frame %0d: NOT PROCESSED", i);
                1: $fdisplay(log_file, "Frame %0d: NORMAL", i);
                2: $fdisplay(log_file, "Frame %0d: ATTACK", i);
            endcase
        end
        $fdisplay(log_file, "-------------------\n");
        
        // Close log file
        $fclose(log_file);
        
        // End simulation
        $finish;
    end
    
    // Timeout to prevent infinite simulation - increased significantly
    initial begin
        #(CLOCK_PERIOD*100000000); // 100,000,000 clock cycles (2000ms at 50MHz)
        $display("Simulation timeout after %0d clock cycles", 100000000);
        $fdisplay(log_file, "Simulation timeout after %0d clock cycles", 100000000);
        
        // Report results even on timeout
        $display("\n--- Test Summary (TIMEOUT) ---");
        $display("Total frames sent: %0d", num_frames);
        $display("Total predictions received: %0d", num_predictions);
        $display("Normal frames: %0d", num_predictions - num_attacks);
        $display("Attack frames: %0d", num_attacks);
        
        // Detailed results for each frame
        $display("\n--- Detailed Frame Results ---");
        for (i = 0; i < num_frames; i = i + 1) begin
            case (frame_results[i])
                0: $display("Frame %0d: NOT PROCESSED", i);
                1: $display("Frame %0d: NORMAL", i);
                2: $display("Frame %0d: ATTACK", i);
            endcase
        end
        
        $fdisplay(log_file, "\n--- Test Summary (TIMEOUT) ---");
        $fdisplay(log_file, "Total frames sent: %0d", num_frames);
        $fdisplay(log_file, "Total predictions received: %0d", num_predictions);
        $fdisplay(log_file, "Total normal frames: %0d", num_predictions - num_attacks);
        $fdisplay(log_file, "Total attack frames: %0d", num_attacks);
        
        // Detailed results for each frame in log
        $fdisplay(log_file, "\n--- Detailed Frame Results ---");
        for (i = 0; i < num_frames; i = i + 1) begin
            case (frame_results[i])
                0: $fdisplay(log_file, "Frame %0d: NOT PROCESSED", i);
                1: $fdisplay(log_file, "Frame %0d: NORMAL", i);
                2: $fdisplay(log_file, "Frame %0d: ATTACK", i);
            endcase
        end
        
        $fclose(log_file);
        $finish;
    end
    
    // Monitor FSM state
    wire [1:0] state;
    assign state = dut.state;
    
    always @(state) begin
        case(state)
            0: begin
                $display("Time %0t: FSM State: IDLE", $time);
                $fdisplay(log_file, "Time %0t: FSM State: IDLE", $time);
            end
            1: begin
                $display("Time %0t: FSM State: COLLECTING", $time);
                $fdisplay(log_file, "Time %0t: FSM State: COLLECTING", $time);
            end
            2: begin
                $display("Time %0t: FSM State: VOTING", $time);
                $fdisplay(log_file, "Time %0t: FSM State: VOTING", $time);
            end
            3: begin
                $display("Time %0t: FSM State: WAIT_PREDICTION", $time);
                $fdisplay(log_file, "Time %0t: FSM State: WAIT_PREDICTION", $time);
            end
        endcase
    end
    
    // Monitor voting process
    always @(posedge clk) begin
        if (dut.state == 2'b10) begin // VOTING state
            $display("Time %0t: Voting for frame %0d, attack_votes=%0d/%0d, threshold=%0d", 
                     $time, dut.current_voting_frame, dut.attack_votes, TREE_COUNT, ATTACK_THRESHOLD);
            $fdisplay(log_file, "Time %0t: Voting for frame %0d, attack_votes=%0d/%0d, threshold=%0d", 
                     $time, dut.current_voting_frame, dut.attack_votes, TREE_COUNT, ATTACK_THRESHOLD);
        end
    end
    
    // Simplified debug task that doesn't access hierarchical paths with variable indices
    task debug_tree_state;
        input integer tree_index;
        begin
            $display("DEBUG: Tree %0d - Debug information requested", tree_index);
            $fdisplay(log_file, "DEBUG: Tree %0d - Debug information requested", tree_index);
            // No hierarchical access with variable index
        end
    endtask
    
endmodule 