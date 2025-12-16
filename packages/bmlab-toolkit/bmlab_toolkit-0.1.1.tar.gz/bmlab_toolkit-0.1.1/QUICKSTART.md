# Quick Start Guide

## Development Setup

```bash
# 1. Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
# venv\Scripts\activate  # On Windows

# 2. Install package in editable mode
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest
```

## Usage

### CLI Command

After installation, the `bmlab-flash` command is available:

```bash
# List connected programmers
bmlab-flash
bmlab-flash --programmer jlink

# Flash with auto-detected JLink (first available)
bmlab-flash firmware.hex

# With specific serial number
bmlab-flash firmware.hex --serial 123456789

# With specific MCU
bmlab-flash firmware.hex --mcu STM32F765ZG

# Specify everything explicitly
bmlab-flash firmware.hex --serial 123456789 --mcu STM32F765ZG --programmer jlink

# Get help
bmlab-flash --help
```

### RTT Communication

Connect to device RTT for real-time communication:

```bash
# Connect with auto-detection
bmlab-jlink-rtt

# Connect to specific device
bmlab-jlink-rtt --serial 123456789 --mcu STM32F765ZG

# Connect via IP address
bmlab-jlink-rtt --ip 192.168.1.100

# Read indefinitely
bmlab-jlink-rtt -t 0

# Send message
bmlab-jlink-rtt --msg "hello\n"

# Get help
bmlab-jlink-rtt --help
```

See [RTT_GUIDE.md](RTT_GUIDE.md) for detailed RTT documentation.

### Python API

#### Flashing

```python
from bmlab_toolkit import JLinkProgrammer

# Create programmer instance
prog = JLinkProgrammer(serial=123456789)

# Flash firmware
prog.flash("firmware.hex")

# Flash with specific MCU
prog.flash("firmware.hex", mcu="STM32F765ZG")
```

#### RTT Communication

```python
from bmlab_toolkit import JLinkProgrammer
import time

prog = JLinkProgrammer(serial=123456789)

try:
    # Connect and start RTT
    prog._connect_target(mcu="STM32F765ZG")
    prog.start_rtt(delay=1.0)
    
    # Send data
    prog.rtt_write(b"Hello!\n")
    
    # Read data
    data = prog.rtt_read()
    if data:
        print(data.decode('utf-8', errors='replace'))
    
    # Stop RTT
    prog.stop_rtt()
finally:
    prog._disconnect_target()
```

## Building Package

```bash
# Install build tool
pip install build

# Build package
python -m build

# Output will be in dist/
```

## Publishing to PyPI

```bash
# Install twine
pip install twine

# Upload to TestPyPI (for testing)
twine upload --repository testpypi dist/*

# Or to main PyPI
twine upload dist/*
```

## Project Structure

```
bmlab_toolkit/
├── src/bmlab_toolkit/       # Main package code
│   ├── __init__.py         # Package API
│   ├── flashing.py         # Flashing functions
│   ├── list_devices.py     # Device detection
│   └── jlink_device_detector.py  # Device detector
├── tests/                   # Tests
├── examples/                # Usage examples
├── pyproject.toml          # Project configuration
└── README.md               # Documentation
```

## Before Publishing

In `pyproject.toml`:
1. Update `authors` - your name and email
2. Update `Homepage` and `Repository` - links to your repository
3. Update `description` if needed

## Dependencies

Main dependencies:
- `pylink-square` - for JLink support (more programmers coming soon)

Development dependencies:
- `pytest` - for testing
- `pytest-cov` - for code coverage
