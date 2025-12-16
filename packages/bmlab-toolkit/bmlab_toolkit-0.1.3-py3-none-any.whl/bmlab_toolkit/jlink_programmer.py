"""
JLink Programmer Implementation

This module provides JLink programmer implementation based on the Programmer abstract class.
Uses pylink-square library for communication with SEGGER J-Link devices.
"""

import logging
import time
import pylink
from typing import Optional, List, Dict, Any
from .programmer import Programmer, DBGMCU_IDCODE_ADDRESSES, DEVICE_ID_MAP, DEFAULT_MCU_MAP

# Configure default logging level for JLinkProgrammer
logging.basicConfig(level=logging.WARNING, format='%(levelname)s - %(message)s')

# Suppress pylink logger to avoid communication timeout errors during disconnect
pylink_logger = logging.getLogger('pylink')
pylink_logger.setLevel(logging.WARNING)


class JLinkProgrammer(Programmer):
    """JLink programmer implementation."""

    def __init__(self, serial: Optional[int] = None, ip_addr: Optional[str] = None, log_level: int = logging.WARNING):
        """
        Initialize JLink programmer.
        
        Args:
            serial: JLink serial number (optional, will auto-detect first available if not provided)
            ip_addr: JLink IP address for network connection (e.g., "192.168.1.100")
            log_level: Logging level (logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR)
        """
        super().__init__(serial)
        self._jlink = pylink.JLink()
        self._mcu = None
        self._rtt_started = False
        self._ip_addr = ip_addr
        
        # Set logging level for this instance
        self.logger.setLevel(log_level)

        # If IP address is provided, use it
        if ip_addr:
            self._serial = None
            print(f"Using JLink at IP: {ip_addr}")
        # If no serial specified, find first available device
        elif serial is None:
            devices = self.scan()
            if not devices:
                raise RuntimeError("No JLink devices found. Please connect a JLink.")
            
            # Show all detected devices
            print(f"Detected {len(devices)} JLink device(s):")
            for i, dev in enumerate(devices):
                product = dev.get('product', 'Unknown')
                target = dev.get('target', 'Not detected')
                print(f"  [{i}] Serial: {dev['serial']}, Product: {product}, Target: {target}")
            
            # Use the first device
            self._serial = devices[0]['serial']
            print(f"Using JLink with serial: {self._serial}")
        else:
            self._serial = serial
            print(f"Selected JLink with serial: {serial}")

    def flash(self, file_path: str, mcu: Optional[str] = None, reset: bool = True) -> bool:
        """
        Flash firmware to the device using JLink.
        Automatically connects to target if not already connected.
        
        Args:
            file_path: Path to firmware file (.hex or .bin)
            mcu: MCU name (optional, will auto-detect if not provided)
            reset: Whether to reset device after flashing (default: True)
            
        Returns:
            True if flash was successful, False otherwise
        """
        try:
            # Always ensure clean connection state
            if self._jlink.opened():
                self.logger.debug("Closing existing connection before flashing")
                self._jlink.close()
            
            # Connect to target
            if not self._connect_target(mcu=mcu):
                self.logger.error("Failed to connect to device")
                return False
            
            self.logger.info(f"Flashing {file_path}...")
            
            # Flash at STM32 default flash base address
            try:
                # Check file extension to determine flashing method
                if not file_path.lower().endswith('.hex') and not file_path.lower().endswith('.bin'):
                    self.logger.error(f"Unsupported file format: {file_path}")
                    return False

                result = self._jlink.flash_file(file_path, 0x08000000)
                if result < 0:
                    self.logger.error(f"Flash failed with result: {result}")
                    return False
                self.logger.info(f"Flash successful: {result} bytes written")
                
            except Exception as e:
                self.logger.error(f"Flash operation failed: {e}")
                return False
            
            # Reset device if requested
            if reset:
                try:
                    self.logger.info("Resetting device...")
                    self.reset(halt=False)
                except Exception as e:
                    self.logger.warning(f"Reset failed: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Flash error: {e}")
            return False
        finally:
            # Disconnect after flashing
            try:
                self._disconnect_target()
            except Exception as e:
                self.logger.warning(f"Disconnect error: {e}")

    def probe(self) -> bool:
        """
        Probe/detect if JLink is connected and accessible.
        
        Returns:
            True if JLink is detected, False otherwise
        """
        try:
            if self._serial:
                # Check if specific serial exists
                emulators = pylink.JLink().connected_emulators()
                return any(emu.SerialNumber == self._serial for emu in emulators)
            else:
                # Check if any JLink is connected
                return True
        except Exception as e:
            self.logger.error(f"Probe error: {e}")
            return False

    def _connect_target(self, mcu: Optional[str] = None) -> bool:
        """
        Connect to the target device via JLink (private method).
        
        Args:
            mcu: MCU name (optional, will auto-detect if not provided)
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Verify device exists before trying to open (skip for IP connections)
            if self._serial:
                temp_jlink = pylink.JLink()
                emulators = temp_jlink.connected_emulators()
                
                found = any(emu.SerialNumber == self._serial for emu in emulators)
                if not found:
                    available = [emu.SerialNumber for emu in emulators]
                    self.logger.error(f"Device {self._serial} not found. Available: {available}")
                    return False
            
            # Open JLink connection (with IP, serial, or first available)
            if self._ip_addr:
                self.logger.info(f"Opening JLink (ip={self._ip_addr})")
                try:
                    self._jlink.open(ip_addr=f"{self._ip_addr}:19020")
                except Exception as e:
                    self.logger.error(f"Failed to open JLink at IP {self._ip_addr}: {e}")
                    return False
            elif self._serial:
                self.logger.info(f"Opening JLink with serial: {self._serial}")
                try:
                    # Try opening without serial first, then set it
                    self._jlink.open()
                    self._jlink.close()
                    self._jlink.open(serial_no=self._serial)
                except Exception as e:
                    self.logger.error(f"Failed to open JLink with serial {self._serial}: {e}")
                    return False
            else:
                self.logger.error(f"No serial or IP specified for JLink connection")
                return False
            
            self._jlink.set_tif(pylink.enums.JLinkInterfaces.SWD)
            if not self._jlink.opened():
                self.logger.error("Failed to open JLink")
                return False

            # Connect to MCU
            if mcu:
                self.logger.info(f"Connecting to specified MCU: {mcu}")
                try:
                    self._jlink.connect(mcu)
                    self._mcu = mcu
                except Exception as e:
                    self.logger.error(f"Failed to connect to {mcu}: {e}")
                    return False
            else:
                self.logger.info("Auto-detecting MCU...")
                try:
                    detected_mcu = self.detect_target()
                    
                    if detected_mcu:
                        self.logger.info(f"Detected MCU: {detected_mcu}")
                        self._mcu = detected_mcu
                        # Disconnect and reconnect with proper device name for correct flash programming
                        if self._jlink.connected():
                            try:
                                # Set device and reconnect for proper configuration
                                self._jlink.exec_command(f"device = {detected_mcu}")
                                self.logger.debug(f"Set device to {detected_mcu}")
                            except Exception as e:
                                self.logger.warning(f"Could not set device: {e}, will use generic connection")
                    else:
                        self.logger.warning("Could not auto-detect MCU, trying generic Cortex-M4")
                        self._mcu = "Cortex-M4"
                        self._jlink.connect(self._mcu)
                except Exception as e:
                    self.logger.error(f"MCU detection/connection failed: {e}")
                    # Try fallback to Cortex-M4
                    try:
                        self.logger.warning("Trying fallback to Cortex-M4")
                        self._mcu = "Cortex-M4"
                        self._jlink.connect(self._mcu)
                    except Exception as e2:
                        self.logger.error(f"Fallback connection also failed: {e2}")
                        return False

            self.logger.info(f"Connected to {self._mcu}")
            print(f"Connected to target: {self._mcu}")
            return True

        except Exception as e:
            self.logger.error(f"Connection error: {e}")
            return False

    def _disconnect_target(self):
        """Disconnect from the target device and close JLink (private method)."""
        try:
            if self._jlink.opened():
                self.logger.info("Disconnecting from device")
                self._jlink.close()
        except pylink.errors.JLinkException as e:
            # Ignore timeout errors during close - known pylink issue on Linux
            if "timed out" not in str(e).lower():
                self.logger.warning(f"Error during disconnect: {e}")
        except Exception as e:
            self.logger.warning(f"Error during disconnect: {e}")
        finally:
            self._mcu = None

    def reset(self, halt: bool = False):
        """
        Reset the target device.
        
        Args:
            halt: Whether to halt after reset
        """
        if not self._jlink.opened():
            self.logger.warning("Not connected, cannot reset")
            return

        try:
            self.logger.info(f"Resetting device (halt={halt})")
            self._jlink.reset(halt=halt)
        except Exception as e:
            self.logger.error(f"Reset error: {e}")

    def erase(self, mcu: Optional[str] = None) -> bool:
        """
        Erase the target device flash memory.
        
        Args:
            mcu: MCU name (optional, will auto-detect if not provided)
            
        Returns:
            True if erase was successful, False otherwise
        """
        try:
            # Always ensure clean connection state
            if self._jlink.opened():
                self.logger.debug("Closing existing connection before erasing")
                self._jlink.close()
            
            # Connect to target
            if not self._connect_target(mcu=mcu):
                self.logger.error("Failed to connect to device")
                return False
            
            self.logger.info("Erasing device flash memory...")
            
            # Halt the core before erasing
            try:
                if not self._jlink.halted():
                    self._jlink.halt()
                    self.logger.debug("Core halted for erasing")
            except Exception as e:
                self.logger.warning(f"Could not halt core: {e}")
            
            # Erase flash
            try:
                self._jlink.erase()
                self.logger.info("Erase successful")
                return True
            except Exception as e:
                self.logger.error(f"Erase operation failed: {e}")
                return False
            
        except Exception as e:
            self.logger.error(f"Erase error: {e}")
            return False
        finally:
            # Disconnect after erasing
            try:
                self._disconnect_target()
            except Exception as e:
                self.logger.warning(f"Disconnect error: {e}")

    @staticmethod
    def scan() -> List[Dict[str, Any]]:
        """
        Get list of all available JLink devices.
        
        Returns:
            List of device information dictionaries:
            - serial: Serial number
            - product: Product name (if available)
            - target: Target MCU name (if detectable)
            - type: 'jlink'
        """
        try:
            jlink = pylink.JLink()
            emulators = jlink.connected_emulators()
            
            devices = []
            for emu in emulators:
                device_info = {
                    'serial': emu.SerialNumber,
                    'type': 'jlink'
                }
                if hasattr(emu, 'acProduct'):
                    # Decode bytes to string if needed
                    product = emu.acProduct
                    if isinstance(product, bytes):
                        product = product.decode('utf-8', errors='ignore')
                    device_info['product'] = product
                
                # Try to detect target MCU
                try:
                    temp_jlink = pylink.JLink()
                    temp_jlink.open(serial_no=emu.SerialNumber)
                    temp_jlink.set_tif(pylink.enums.JLinkInterfaces.SWD)
                    
                    # Create temporary programmer instance to use detect_target
                    temp_programmer = JLinkProgrammer.__new__(JLinkProgrammer)
                    temp_programmer._jlink = temp_jlink
                    temp_programmer.logger = logging.getLogger(__name__)
                    
                    detected = temp_programmer.detect_target()
                    if detected:
                        device_info['target'] = detected
                    
                    temp_jlink.close()
                except Exception:
                    # If detection fails, just skip it
                    pass
                
                devices.append(device_info)
            
            if jlink.opened():
                jlink.close()
                
            return devices
        except Exception as e:
            print(f"Warning: Could not enumerate JLink devices: {e}")
            return []
    
    @staticmethod
    def scan_network(network: str, start_ip: Optional[int] = None, end_ip: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Scan network for JLink Remote Servers.
        
        Args:
            network: Network in CIDR notation (e.g., '192.168.1.0/24')
            start_ip: Starting last octet for IP range (optional)
            end_ip: Ending last octet for IP range (optional)
            
        Returns:
            List of device information dictionaries:
            - ip: IP address
            - target: Target MCU name (if detectable)
            - type: 'jlink-remote'
        """
        import ipaddress
        import socket
        
        def check_ip(ip_str):
            """Check if JLink Remote Server is available at IP."""
            # First check if port 19020 is open using socket (fast and safe)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)  # 500ms timeout
            
            try:
                result = sock.connect_ex((ip_str, 19020))
                sock.close()
                
                if result != 0:
                    # Port is not open, skip
                    return None
                
                # Port is open, try JLink connection
                temp_jlink = pylink.JLink()
                temp_jlink.open(ip_addr=f"{ip_str}:19020")
                
                if temp_jlink.opened():
                    device_info = {
                        'ip': ip_str,
                        'type': 'jlink-remote'
                    }
                    
                    # Try to detect target
                    try:
                        temp_jlink.set_tif(pylink.enums.JLinkInterfaces.SWD)
                        
                        temp_programmer = JLinkProgrammer.__new__(JLinkProgrammer)
                        temp_programmer._jlink = temp_jlink
                        temp_programmer.logger = logging.getLogger(__name__)
                        
                        detected = temp_programmer.detect_target()
                        if detected:
                            device_info['target'] = detected
                        else:
                            device_info['target'] = 'Connected'
                    except Exception:
                        device_info['target'] = 'Connected'
                    
                    try:
                        temp_jlink.close()
                    except pylink.errors.JLinkException as e:
                        # Ignore timeout errors during disconnect
                        if 'Communication timed out' not in str(e):
                            pass
                    except Exception:
                        pass
                    
                    return device_info
            except Exception:
                try:
                    sock.close()
                except:
                    pass
            
            return None
        
        try:
            net = ipaddress.ip_network(network, strict=False)
            # Generate list of IPs to scan
            ips = [str(ip) for ip in net.hosts()]
            
            # Filter by start/end IP if specified
            if start_ip is not None or end_ip is not None:
                filtered_ips = []
                for ip_str in ips:
                    last_octet = int(ip_str.split('.')[-1])
                    if start_ip is not None and last_octet < start_ip:
                        continue
                    if end_ip is not None and last_octet > end_ip:
                        continue
                    filtered_ips.append(ip_str)
                ips = filtered_ips
            
            devices = []
            total = len(ips)
            
            print(f"Scanning {total} IP addresses...")
            
            # Sequential scanning
            for idx, ip in enumerate(ips, 1):
                print(f"  [{idx}/{total}] {ip}...", end='', flush=True)
                result = check_ip(ip)
                if result:
                    devices.append(result)
                    print(f" ✓ Found: {result.get('target', 'Unknown')}")
                else:
                    print(" -")
            
            return devices
        except Exception as e:
            print(f"Warning: Network scan failed: {e}")
            return []

    def read_target_memory(self, address: int, num_bytes: int) -> Optional[list]:
        """
        Read memory from target device.
        
        Args:
            address: Memory address to read from
            num_bytes: Number of bytes to read
            
        Returns:
            List of bytes or None on error
        """
        if not self._jlink.opened():
            self.logger.error("Not connected to device")
            return None

        try:
            return self._jlink.memory_read(address, num_bytes)
        except Exception as e:
            self.logger.error(f"Memory read error: {e}")
            return None

    def detect_target(self) -> Optional[str]:
        """
        Detect STM32 device by reading DBGMCU_IDCODE register.
        
        Tries to connect with different Cortex-M cores and read device ID.
            
        Returns:
            Device name like 'STM32F765ZG' or 'STM32F103RE', or None if detection failed
        """
        # Try to connect with different Cortex-M cores
        # Order: M7 -> M4 -> M3 -> M0 (from most complex to simplest, as modern MCUs are more common)
        connected_core = None
        
        for core in ['Cortex-M7', 'Cortex-M4', 'Cortex-M3', 'Cortex-M0']:
            try:
                self.logger.debug(f"Trying to connect with {core}...")
                self._jlink.connect(core, verbose=False)
                
                # Try to read IDCODE to verify connection works
                try:
                    test_read = self._jlink.memory_read32(0xE0042000, 1)[0]
                    if test_read != 0 and test_read != 0xFFFFFFFF:
                        connected_core = core
                        self.logger.info(f"Successfully connected with {core}")
                        break
                except:
                    pass  # Connection didn't work, try next core
                    
            except Exception as e:
                self.logger.debug(f"Failed to connect with {core}: {e}")
                continue
        
        if not connected_core:
            self.logger.error("Could not connect with any Cortex-M core")
            return None

        try:
            # Try to read device ID from different addresses
            idcode = 0
            found_addr = None
            
            for addr, desc in DBGMCU_IDCODE_ADDRESSES.items():
                try:
                    idcode = self._jlink.memory_read32(addr, 1)[0]
                    if idcode != 0 and idcode != 0xFFFFFFFF:
                        self.logger.info(f"✓ Read IDCODE from 0x{addr:08X} ({desc})")
                        found_addr = addr
                        break
                    else:
                        self.logger.debug(f"✗ Address 0x{addr:08X} returned invalid IDCODE (0x{idcode:08X}) - skipping {desc}")
                except Exception as e:
                    self.logger.debug(f"✗ Cannot read from 0x{addr:08X} ({desc}): {e}")
                    continue
            
            if idcode == 0 or idcode == 0xFFFFFFFF or found_addr is None:
                self.logger.error("Could not read valid IDCODE from any known address")
                return None
            
            # Extract device and revision IDs
            dev_id = (idcode >> 0) & 0xFFF
            rev_id = (idcode >> 16) & 0xFFFF
            
            self.logger.info(f"Detected Device ID: 0x{dev_id:03X}, Revision ID: 0x{rev_id:04X}")
            
            # Get device family name
            device_family = DEVICE_ID_MAP.get(dev_id, f"Unknown (0x{dev_id:03X})")
            self.logger.info(f"Device Family: {device_family}")
            
            # Get default MCU name for this device ID
            mcu_name = DEFAULT_MCU_MAP.get(dev_id)
            
            if mcu_name is None:
                # Return generic name based on family if no specific default
                mcu_name = device_family.replace(" ", "_")
            
            return mcu_name
            
        except Exception as e:
            self.logger.warning(f"Could not detect device automatically: {e}")
            return None

    def start_rtt(self, mcu: Optional[str] = None, reset: bool = True, rtt_address: Optional[int] = None, delay: float = 1.0) -> bool:
        """
        Start Real-Time Transfer (RTT) communication.
        Connects to target if not already connected.
        
        Args:
            mcu: MCU name (optional, will auto-detect if not provided)
            reset: Whether to reset target before starting RTT
            rtt_address: RTT control block address (None for auto-search)
            delay: Delay after starting RTT in seconds
            
        Returns:
            True if RTT started successfully, False otherwise
        """
        # Connect to target if not already connected
        if self._jlink.opened():
            self._jlink.close()
        
        if not self._connect_target(mcu=mcu):
            self.logger.error("Failed to connect to target")
            return False
        
        # Reset if requested
        if reset:
            self.logger.info("Resetting target before RTT...")
            self.reset(halt=False)
            time.sleep(0.5)  # Give device time to restart
        
        try:
            if rtt_address:
                self.logger.info(f"Starting RTT at address 0x{rtt_address:08X}")
                self._jlink.rtt_start(rtt_address)
            else:
                self.logger.info("Starting RTT with auto-search")
                self._jlink.rtt_start()
            
            # Give RTT time to initialize
            time.sleep(delay)
            self._rtt_started = True
            self.logger.info("RTT started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start RTT: {e}")
            return False
    
    def stop_rtt(self):
        """Stop RTT communication."""
        if self._rtt_started:
            try:
                self._jlink.rtt_stop()
                self._rtt_started = False
                self.logger.info("RTT stopped")
            except Exception as e:
                self.logger.warning(f"Error stopping RTT: {e}")
    
    def rtt_read(self, buffer_index: int = 0, max_bytes: int = 4096) -> bytes:
        """
        Read data from RTT buffer.
        
        Args:
            buffer_index: RTT buffer index (0 for default up buffer)
            max_bytes: Maximum number of bytes to read
            
        Returns:
            Bytes read from RTT buffer
            
        Raises:
            Exception: If RTT read fails (e.g., connection lost)
        """
        if not self._rtt_started:
            self.logger.warning("RTT not started")
            return b""
        
        try:
            data = self._jlink.rtt_read(buffer_index, max_bytes)
            return bytes(data) if data else b""
        except Exception as e:
            self.logger.error(f"RTT read error: {e}")
            raise
    
    def rtt_write(self, data: bytes, buffer_index: int = 0) -> int:
        """
        Write data to RTT buffer.
        
        Args:
            data: Data to write
            buffer_index: RTT buffer index (0 for default down buffer)
            
        Returns:
            Number of bytes written
        """
        if not self._rtt_started:
            self.logger.warning("RTT not started")
            return 0
        
        try:
            return self._jlink.rtt_write(buffer_index, data)
        except Exception as e:
            self.logger.error(f"RTT write error: {e}")
            return 0
