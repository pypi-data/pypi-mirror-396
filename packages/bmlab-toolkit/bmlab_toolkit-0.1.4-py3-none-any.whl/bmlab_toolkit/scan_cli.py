"""
Device Scanner CLI

Command-line interface for scanning and listing available programmers.
"""

import sys
import argparse
import logging
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed
from .constants import SUPPORTED_PROGRAMMERS, DEFAULT_PROGRAMMER, PROGRAMMER_JLINK
from .jlink_programmer import JLinkProgrammer
import socket
import time

def scan_network_ip(ip_str, log_level):
    """Scan a single IP for JLink Remote Server."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)  # 500ms timeout
    
    try:
        result = sock.connect_ex((ip_str, 19020))
        sock.close()
        time.sleep(1.0)
        
        if result != 0:
            # Port is not open, skip
            return None
    except Exception as e:
        # Connection or detection failed
        return None

    # Try to connect and detect MCU
    prog = None
    try:
        prog = JLinkProgrammer(ip_addr=ip_str, log_level=log_level)
        mcu = prog.connect_target()
        if not mcu:
            # Connection failed
            prog._jlink.close()
            print(f"{ip_str}: No target detected")
            return None
        
        # Successfully connected - get device info
        device_info = {
            'ip': ip_str,
            'type': 'jlink-remote',
            'status': 'Connected',
            'target': mcu if mcu else 'Unknown'
        }
        
        return device_info
    except Exception as e:
        # Connection or detection failed
        return None
    finally:
        # Always close the connection
        try:
            prog.disconnect_target()
        except:
            pass


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
                
                # Generate list of IPs to scan
                ips = [str(ip) for ip in network.hosts()]
                
                # Filter by start/end IP if specified
                if args.start_ip is not None or args.end_ip is not None:
                    filtered_ips = []
                    for ip_str in ips:
                        last_octet = int(ip_str.split('.')[-1])
                        if args.start_ip is not None and last_octet < args.start_ip:
                            continue
                        if args.end_ip is not None and last_octet > args.end_ip:
                            continue
                        filtered_ips.append(ip_str)
                    ips = filtered_ips
                
                total = len(ips)
                print(f"Scanning {total} IP addresses...")
                
                devices = []
                
                # Parallel scanning with ThreadPoolExecutor
                with ThreadPoolExecutor(max_workers=total) as executor:
                    # Submit all IP checks
                    future_to_ip = {executor.submit(scan_network_ip, ip, log_level): ip for ip in ips}
                    
                    # Process results as they complete
                    completed = 0
                    for future in as_completed(future_to_ip):
                        ip = future_to_ip[future]
                        completed += 1
                        try:
                            # Timeout for each future (e.g., 5 seconds)
                            result = future.result(timeout=5)
                            if result:
                                devices.append(result)
                                print(f"  [{completed}/{total}] {ip} ✓ Found")
                            else:
                                print(f"  [{completed}/{total}] {ip} -")
                        except Exception as e:
                            print(f"  [{completed}/{total}] {ip} ✗ Error: {e}")
                        except TimeoutError:
                            print(f"  [{completed}/{total}] {ip} ✗ Timeout (skipped)")
                
                if not devices:
                    print("\nNo JLink Remote Servers found on the network.")
                    sys.exit(1)
                
                print(f"\nFound {len(devices)} JLink Remote Server(s):\n")
                for i, dev in enumerate(devices):
                    ip = dev.get('ip', 'Unknown')
                    status = dev.get('status', 'Unknown')
                    target = dev.get('target', 'Unknown')
                    
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
