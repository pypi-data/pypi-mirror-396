"""
JLink RTT CLI

Command-line interface for connecting to JLink RTT and reading/writing data.
"""

import sys
import time
import argparse
import logging
from typing import Optional
from .jlink_programmer import JLinkProgrammer


def main():
    """Main entry point for bmlab-jlink-rtt command."""
    parser = argparse.ArgumentParser(
        description='Connect to JLink RTT for real-time data transfer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Connect with auto-detect and read for 10 seconds
  bmlab-jlink-rtt

  # Specify JLink serial number
  bmlab-jlink-rtt --serial 123456789

  # Connect via IP address (MCU not needed)
  bmlab-jlink-rtt --ip 192.168.1.100

  # Specify MCU explicitly
  bmlab-jlink-rtt --mcu STM32F765ZG

  # Read indefinitely until Ctrl+C
  bmlab-jlink-rtt -t 0

  # Send message after connection
  bmlab-jlink-rtt --msg "hello\\n"

  # Send message after 2 seconds delay
  bmlab-jlink-rtt --msg "test" --msg-timeout 2.0

  # No reset on connection
  bmlab-jlink-rtt --no-reset
        """
    )
    
    parser.add_argument('--serial', '-s', type=str, default=None,
                       help='JLink serial number (auto-detect if not provided)')
    
    parser.add_argument('--ip', type=str, default=None,
                       help='JLink IP address for network connection (e.g., 192.168.1.100)')
    
    parser.add_argument('--mcu', '-m', type=str, default=None,
                       help='MCU name (e.g., STM32F765ZG). Auto-detects if not provided. Not used with --ip.')
    
    parser.add_argument('--reset', dest='reset', action='store_true', default=True,
                       help='Reset target after connection (default: True)')
    
    parser.add_argument('--no-reset', dest='reset', action='store_false',
                       help='Do not reset target after connection')
    
    parser.add_argument('--timeout', '-t', type=float, default=10.0,
                       help='Read timeout in seconds. 0 means read until interrupted (default: 10.0)')
    
    parser.add_argument('--msg', type=str, default=None,
                       help='Message to send via RTT after connection')
    
    parser.add_argument('--msg-timeout', type=float, default=0.5,
                       help='Delay in seconds before sending message (default: 0.5)')
    
    parser.add_argument('--msg-retries', type=int, default=10,
                       help='Number of retries for sending message (default: 10)')
    
    parser.add_argument('--log-level', '-l', type=str, default='WARNING',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Set logging level (default: WARNING)')
    
    args = parser.parse_args()
    
    # Validate that --serial and --ip are mutually exclusive
    if args.serial and args.ip:
        print("Error: Cannot specify both --serial and --ip")
        sys.exit(1)
    
    # Convert serial to int if provided
    serial = None
    if args.serial:
        try:
            serial = int(args.serial)
        except ValueError:
            print(f"Error: Invalid serial number: {args.serial}")
            sys.exit(1)
    
    ip_addr = args.ip
    
    try:
        # Convert log level string to logging constant
        log_level = getattr(logging, args.log_level.upper())
        
        # Create programmer instance
        prog = JLinkProgrammer(serial=serial, ip_addr=ip_addr, log_level=log_level)
        
        # Start RTT (will connect and reset if needed)
        # When using IP, MCU is not specified (will use generic connection)
        mcu = None if ip_addr else args.mcu
        
        if not prog.start_rtt(mcu=mcu, reset=args.reset, delay=1.0):
            print("Error: Failed to start RTT")
            sys.exit(1)
        
        print("RTT connected. Reading data...")
        if args.timeout == 0:
            print("(Press Ctrl+C to stop)")
        else:
            print(f"(Reading for {args.timeout} seconds)")
        
        # Send message if provided
        if args.msg:
            time.sleep(args.msg_timeout)
            
            # Convert escape sequences
            msg = args.msg.encode('utf-8').decode('unicode_escape').encode('utf-8')
            
            # Try to send with retries
            max_retries = args.msg_retries
            retry_delay = 1.0
            bytes_written = 0
            
            for attempt in range(max_retries):
                bytes_written = prog.rtt_write(msg)
                if bytes_written > 0:
                    break
                
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
            else:
                print(f"Warning: Failed to write message after {max_retries} attempts")
        
        # Read data
        start_time = time.time()
        try:
            while True:
                # Check timeout
                if args.timeout > 0:
                    elapsed = time.time() - start_time
                    if elapsed >= args.timeout:
                        break
                
                # Read RTT data
                try:
                    data = prog.rtt_read(max_bytes=4096)
                except Exception as e:
                    print(f"\nRTT connection lost: {e}")
                    break
                
                if data:
                    # Print data to stdout
                    try:
                        text = data.decode('utf-8', errors='replace')
                        print(text, end='', flush=True)
                    except Exception:
                        # If decode fails, print raw bytes
                        print(data, flush=True)
                
                # Small delay to avoid busy-waiting
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
        
        # Cleanup
        prog.stop_rtt()
        prog.disconnect_target()
        
        print("\nDone.")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
