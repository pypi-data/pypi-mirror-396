# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-12-11

### Fixed
- **Linux Segmentation Fault with IP Connections** - Fixed critical bug causing segfault on Linux when using `bmlab-jlink-rtt --ip`
  - Skip USB device enumeration for IP connections (not applicable for network JLink)
  - Skip `set_tif()` and `connect()` calls for IP connections (handled by JLink Remote Server)
  - Skip `reset()` operation for IP connections to avoid crashes
  - IP connections now use remote server's existing target connection instead of attempting reconnection

### Changed
- Improved IP connection handling for better stability on Linux systems
- IP connections now display "Remote Target" as MCU name when not explicitly specified

## [0.1.0] - 2025-11-22

### Added
- Command-line interface with `bmlab-flash` command
- `bmlab-erase` command for erasing device flash memory
- `erase()` method in Programmer base class and JLinkProgrammer implementation
- Device erase CLI with support for auto-detection and manual configuration
- Support for erasing via IP address connection

- **RTT Message Sending** - Added retry logic for RTT write operations
  - `bmlab-jlink-rtt` CLI command for real-time device communication
  - `start_rtt()` method to initiate RTT communication
  - `stop_rtt()` method to stop RTT communication
  - `rtt_read()` method to read data from RTT buffers
  - `rtt_write()` method to write data to RTT buffers
  - Support for custom RTT control block addresses
  - Configurable timeouts and delays
  - `--msg-retries` parameter (default: 10) for configurable retry attempts
  - Automatic retry with 1-second delay between attempts
  - Warning message if all retry attempts fail
  - Verbose mode shows retry attempts and success status

- **RTT CLI Features**:
  - Auto-detection of JLink serial and MCU (or specify explicitly)
  - Configurable read timeout (default 10s, 0 for indefinite)
  - Send messages to device via `--msg` parameter
  - Configurable message send delay with `--msg-timeout`
  - Optional target reset control (`--reset` / `--no-reset`)
  - Verbose mode for debugging with `-v` flag
  - Escape sequence support in messages (e.g., `\n`, `\t`)

- **Network JLink Support** - Added ability to connect to JLink via IP address
  - `--ip` parameter in both `bmlab-flash` and `bmlab-jlink-rtt` CLI commands
  - `ip_addr` parameter in `JLinkProgrammer` constructor
  - Connection format: `jlink.open(ip_addr="192.168.1.100:19020")`
  - When using IP connection, MCU parameter is not required
  - `--serial` and `--ip` are mutually exclusive parameters
  - Full support for flashing and RTT communication over network
