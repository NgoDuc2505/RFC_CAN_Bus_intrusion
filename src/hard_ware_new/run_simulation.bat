@echo off
echo Running Random Forest Simulation...

rem Clean up previous simulation files
del *.vcd 2>nul
del *.log 2>nul
del *.out 2>nul

rem Compile the design
echo Compiling design files...
iverilog -o random_forest_sim.out -g2012 -Wall Random_forest_top_new.v random_forest_top_tb.v

rem Check if compilation was successful
if %errorlevel% neq 0 (
    echo ERROR: Compilation failed!
    exit /b %errorlevel%
)

echo Compilation successful!

rem Run the simulation
echo Running simulation...
vvp random_forest_sim.out

rem Check if simulation was successful
if %errorlevel% neq 0 (
    echo ERROR: Simulation failed!
    exit /b %errorlevel%
)

echo Simulation completed!

rem Open the waveform viewer if GTKWave is installed
where gtkwave >nul 2>nul
if %errorlevel% equ 0 (
    echo Opening waveform in GTKWave...
    start gtkwave dump.vcd
) else (
    echo GTKWave not found. Skipping waveform display.
)

rem Display log file summary
echo.
echo Log file summary:
echo -----------------
findstr /C:"File opened successfully" random_forest_results.log
findstr /C:"Loaded" random_forest_results.log
findstr /C:"ERROR" random_forest_results.log
findstr /C:"WARNING" random_forest_results.log
findstr /C:"FSM State" random_forest_results.log | findstr /C:"COLLECTING"
findstr /C:"FSM State" random_forest_results.log | findstr /C:"VOTING"
findstr /C:"FSM State" random_forest_results.log | findstr /C:"WAIT_PREDICTION"
findstr /C:"Prediction" random_forest_results.log
findstr /C:"VOTE_COMPLETE" random_forest_results.log
findstr /C:"VOTING_DECISION" random_forest_results.log
findstr /C:"Timeout" random_forest_results.log
findstr /C:"collecting_timeout_counter" random_forest_results.log | findstr /C:"10000"

echo.
echo Check for invalid child pointers:
findstr /C:"invalid child pointers" random_forest_results.log

echo.
echo Check for forced leaf nodes:
findstr /C:"forcing leaf node" random_forest_results.log

echo.
echo Check for timeout in COLLECTING state:
findstr /C:"Timeout in COLLECTING state" random_forest_results.log

echo.
echo Done! 