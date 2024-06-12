@echo off
REM Build the production Docker container

REM Check if Dockerfile path is provided
IF "%~1"=="" (
    echo Usage: prod_container_build.cmd path\to\Dockerfile.prod
    exit /B 1
)

SET DOCKERFILE_PATH=%~1

REM Get the directory of the provided Dockerfile
SET DOCKERFILE_DIR=%~dp1

REM Convert the Dockerfile path and directory to Unix-style paths for Docker
FOR /f "tokens=*" %%i IN ('wsl wslpath "%DOCKERFILE_PATH%"') DO SET DOCKERFILE_PATH_UNIX=%%i
FOR /f "tokens=*" %%i IN ('wsl wslpath "%DOCKERFILE_DIR%"') DO SET DOCKERFILE_DIR_UNIX=%%i

REM Build the Docker image
docker build -f %DOCKERFILE_PATH_UNIX% %DOCKERFILE_DIR_UNIX% -t prod-environment .

IF %ERRORLEVEL% NEQ 0 (
    echo Docker build failed
    exit /B 1
)

echo Docker build completed successfully
