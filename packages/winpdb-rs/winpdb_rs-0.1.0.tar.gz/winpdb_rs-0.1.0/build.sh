#!/usr/bin/env bash
# Build script for winpdb_rs
# Requires: Rust toolchain (rustup), Python 3.8+, maturin

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check for Rust
if ! command -v cargo &> /dev/null; then
    echo "Error: Rust not found. Install from https://rustup.rs/"
    exit 1
fi

# Check for maturin
if ! python -m maturin --version &> /dev/null; then
    echo "Installing maturin..."
    pip install maturin
fi

# Build mode
MODE="${1:-release}"

if [ "$MODE" = "dev" ] || [ "$MODE" = "debug" ]; then
    echo "Building in development mode..."
    maturin develop
elif [ "$MODE" = "release" ]; then
    echo "Building in release mode..."
    maturin develop --release
elif [ "$MODE" = "wheel" ]; then
    echo "Building wheel..."
    maturin build --release
    echo "Wheel built in target/wheels/"
else
    echo "Usage: $0 [dev|release|wheel]"
    exit 1
fi

echo "Done!"
