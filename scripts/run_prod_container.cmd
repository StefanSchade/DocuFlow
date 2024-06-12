@echo off
REM Script to run the production Docker container

REM Check if data directory argument is provided
if "%1"=="" (
    echo Usage: run_prod_container.cmd [data_directory_path] [script_arguments...]
    exit /b 1
)

REM Get the absolute path of the data directory
set DATA_DIR=%~1
echo Data directory: %DATA_DIR%

REM Shift the first argument (data directory) and pass the rest to the script
shift

REM Initialize SCRIPT_ARGS variable
set SCRIPT_ARGS=

REM Loop through the remaining arguments and append them to SCRIPT_ARGS
:loop
if "%1"=="" goto endloop
    set SCRIPT_ARGS=%SCRIPT_ARGS% %1
    shift
    goto loop
:endloop

echo Additional arguments: %SCRIPT_ARGS%

REM Change to the project root directory
cd %~dp0..

REM Start the production container with additional script arguments
docker run -it --rm -v "%DATA_DIR%:/workspace/data" prod-environment %SCRIPT_ARGS%

pause
