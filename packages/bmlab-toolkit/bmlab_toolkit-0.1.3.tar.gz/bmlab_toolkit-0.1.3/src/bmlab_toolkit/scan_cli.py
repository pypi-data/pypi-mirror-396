"""
Device Scanner CLI

Command-line interface for scanning and listing available programmers.
"""

import sys
import argparse
import logging
import ipaddress
from .constants import SUPPORTED_PROGRAMMERS, DEFAULT_PROGRAMMER, PROGRAMMER_JLINK
from .jlink_programmer import JLinkProgrammer


def main():
    """Main entry point for bmlab-scan command."""
    parser = argparse.ArgumentParser(
        description='Scan and list available programmers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan for USB JLink programmers
  bmlab-scan

  # Scan network for JLink Remote Servers
  bmlab-scan --network 192.168.1.0/24

  # Scan with debug output
  bmlab-scan --log-level DEBUG
        """
    )
    
    parser.add_argument(
        '--network', '-n',
        type=str,
        default=None,
        help='Network to scan for JLink Remote Servers (e.g., 192.168.1.0/24)'
    )
    
    parser.add_argument(
        '--start-ip',
        type=int,
        default=None,
        help='Starting last octet for IP range (e.g., 100 for x.x.x.100)'
    )
    
    parser.add_argument(
        '--end-ip',
        type=int,
        default=None,
        help='Ending last octet for IP range (e.g., 150 for x.x.x.150)'
    )
    
    parser.add_argument(
        '--programmer', '-p',
        type=str,
        default=DEFAULT_PROGRAMMER,
        choices=SUPPORTED_PROGRAMMERS,
        help=f'Programmer type to scan for (default: {DEFAULT_PROGRAMMER})'
    )
    
    parser.add_argument(
        '--log-level', '-l',
        type=str,
        default='WARNING',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Set logging level (default: WARNING)'
    )
    
    args = parser.parse_args()
    
    try:
        # Convert log level string to logging constant
        log_level = getattr(logging, args.log_level.upper())
        
        # Configure logging
        logging.basicConfig(level=log_level, format='%(levelname)s - %(message)s')
        
        if args.programmer.lower() == PROGRAMMER_JLINK:
            # Network scan mode
            if args.network:
                try:
                    network = ipaddress.ip_network(args.network, strict=False)
                except ValueError as e:
                    print(f"Error: Invalid network format: {e}")
                    sys.exit(1)
                
                print(f"Scanning network {network} for JLink Remote Servers...\n")
                
                devices = JLinkProgrammer.scan_network(str(network), start_ip=args.start_ip, end_ip=args.end_ip)
                
                if not devices:
                    print("No JLink Remote Servers found on the network.")
                    sys.exit(1)
                
                print(f"Found {len(devices)} JLink Remote Server(s):\n")
                for i, dev in enumerate(devices):
                    ip = dev.get('ip', 'Unknown')
                    target = dev.get('target', 'Not detected')
                    
                    print(f"[{i}] JLink Remote Server")
                    print(f"    IP:      {ip}")
                    print(f"    Target:  {target}")
                    print()
                return  # Exit after network scan
            
            # USB scan mode
            else:
                devices = JLinkProgrammer.scan()
            
            if not devices:
                print("No JLink devices found.")
                sys.exit(1)
            
            print(f"Found {len(devices)} JLink device(s):\n")
            for i, dev in enumerate(devices):
                product = dev.get('product', 'Unknown')
                target = dev.get('target', 'Not detected')
                serial = dev['serial']
                
                print(f"[{i}] JLink Programmer")
                print(f"    Serial:  {serial}")
                print(f"    Product: {product}")
                print(f"    Target:  {target}")
                print()
        else:
            print(f"Error: Programmer '{args.programmer}' is not yet implemented")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nScan cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
