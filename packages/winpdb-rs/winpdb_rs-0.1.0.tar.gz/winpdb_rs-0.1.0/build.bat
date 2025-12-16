@echo off
REM Build script for winpdb_rs on Windows
REM Requires: Rust toolchain, Python 3.8+, maturin

setlocal enabledelayedexpansion

cd /d "%~dp0"

REM Check for cargo
where cargo >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Rust not found. Install from https://rustup.rs/
    exit /b 1
)

REM Check for maturin
python -m maturin --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing maturin...
    pip install maturin
)

REM Build mode
set MODE=%1
if "%MODE%"=="" set MODE=release

if "%MODE%"=="dev" (
    echo Building in development mode...
    maturin develop
) else if "%MODE%"=="debug" (
    echo Building in development mode...
    maturin develop
) else if "%MODE%"=="release" (
    echo Building in release mode...
    maturin develop --release
) else if "%MODE%"=="wheel" (
    echo Building wheel...
    maturin build --release
    echo Wheel built in target\wheels\
) else (
    echo Usage: %0 [dev^|release^|wheel]
    exit /b 1
)

echo Done!
