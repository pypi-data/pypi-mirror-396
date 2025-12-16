"""Wireless adapter management with multi-adapter support."""

import subprocess
import re
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class WirelessAdapter:
    """Represents a wireless network adapter."""
    interface: str
    chipset: str = "Unknown"
    driver: str = "Unknown"
    mac_address: str = "Unknown"
    original_mac: str = "Unknown"
    mode: str = "managed"
    channel: Optional[int] = None
    is_monitor: bool = False

class AdapterManager:
    """Manages wireless network adapters."""
    
    def __init__(self, logger):
        self.logger = logger
        self.adapters: Dict[str, WirelessAdapter] = {}
        self.monitor_adapters: List[str] = []
    
    def scan_adapters(self) -> List[WirelessAdapter]:
        """Scan for available wireless adapters."""
        self.logger.info("Scanning for wireless adapters...")
        adapters = []
        
        try:
            result = subprocess.run(['iwconfig'], capture_output=True, text=True, timeout=5)
            
            current_interface = None
            for line in result.stdout.split('\n'):
                if line and not line.startswith(' '):
                    match = re.match(r'^(\w+)\s+', line)
                    if match:
                        current_interface = match.group(1)
                        adapter = self._get_adapter_details(current_interface)
                        if adapter:
                            adapters.append(adapter)
                            self.adapters[adapter.interface] = adapter
            
            self.logger.success(f"Found {len(adapters)} wireless adapter(s)")
            return adapters
        except Exception as e:
            self.logger.error(f"Error scanning adapters: {e}")
            return []
    
    def _get_adapter_details(self, interface: str) -> Optional[WirelessAdapter]:
        """Get detailed information about an adapter."""
        try:
            mac_result = subprocess.run(
                ['ip', 'link', 'show', interface],
                capture_output=True, text=True, timeout=5
            )
            
            mac_match = re.search(r'link/ether\s+([0-9a-f:]+)', mac_result.stdout)
            mac_address = mac_match.group(1) if mac_match else 'Unknown'
            
            mode = 'managed'
            is_monitor = False
            
            iwconfig_result = subprocess.run(['iwconfig', interface], capture_output=True, text=True, timeout=5)
            if 'Mode:Monitor' in iwconfig_result.stdout:
                mode = 'monitor'
                is_monitor = True
            
            return WirelessAdapter(
                interface=interface,
                mac_address=mac_address,
                original_mac=mac_address,
                mode=mode,
                is_monitor=is_monitor
            )
        except Exception as e:
            self.logger.error(f"Error getting details for {interface}: {e}")
            return None
    
    def enable_monitor_mode(self, interface: str) -> bool:
        """Enable monitor mode on an adapter."""
        try:
            self.logger.info(f"Enabling monitor mode on {interface}...")
            
            subprocess.run(['airmon-ng', 'check', 'kill'], capture_output=True, timeout=10)
            result = subprocess.run(['airmon-ng', 'start', interface], capture_output=True, text=True, timeout=10)
            
            monitor_interface = None
            for possible_name in [f"{interface}mon", f"{interface}M", interface]:
                check_result = subprocess.run(['iwconfig', possible_name], capture_output=True, text=True, timeout=5)
                if 'Mode:Monitor' in check_result.stdout:
                    monitor_interface = possible_name
                    break
            
            if monitor_interface:
                if interface in self.adapters:
                    self.adapters[interface].is_monitor = True
                    self.adapters[interface].mode = 'monitor'
                    self.adapters[interface].interface = monitor_interface
                    self.monitor_adapters.append(monitor_interface)
                
                self.logger.success(f"Monitor mode enabled on {monitor_interface}")
                return True
            else:
                self.logger.error(f"Failed to enable monitor mode on {interface}")
                return False
        except Exception as e:
            self.logger.error(f"Error enabling monitor mode: {e}")
            return False
    
    def disable_monitor_mode(self, interface: str) -> bool:
        """Disable monitor mode on an adapter."""
        try:
            self.logger.info(f"Disabling monitor mode on {interface}...")
            subprocess.run(['airmon-ng', 'stop', interface], capture_output=True, timeout=10)
            
            if interface in self.monitor_adapters:
                self.monitor_adapters.remove(interface)
            
            self.logger.success(f"Monitor mode disabled on {interface}")
            return True
        except Exception as e:
            self.logger.error(f"Error disabling monitor mode: {e}")
            return False
    
    def spoof_mac(self, interface: str, random: bool = True, mac: str = None) -> bool:
        """Spoof MAC address of an adapter."""
        try:
            subprocess.run(['ip', 'link', 'set', interface, 'down'], capture_output=True, timeout=5)
            
            if random:
                subprocess.run(['macchanger', '-r', interface], capture_output=True, timeout=5)
            elif mac:
                subprocess.run(['macchanger', '-m', mac, interface], capture_output=True, timeout=5)
            
            subprocess.run(['ip', 'link', 'set', interface, 'up'], capture_output=True, timeout=5)
            
            adapter = self._get_adapter_details(interface)
            if adapter and interface in self.adapters:
                self.adapters[interface].mac_address = adapter.mac_address
            
            self.logger.success(f"MAC address spoofed on {interface}")
            return True
        except Exception as e:
            self.logger.error(f"Error spoofing MAC: {e}")
            return False
    
    def restore_mac(self, interface: str) -> bool:
        """Restore original MAC address."""
        if interface not in self.adapters:
            return False
        
        original_mac = self.adapters[interface].original_mac
        return self.spoof_mac(interface, random=False, mac=original_mac)
    
    def set_channel(self, interface: str, channel: int) -> bool:
        """Set channel for an adapter."""
        try:
            subprocess.run(['iwconfig', interface, 'channel', str(channel)], capture_output=True, timeout=5)
            
            if interface in self.adapters:
                self.adapters[interface].channel = channel
            
            self.logger.debug(f"Set {interface} to channel {channel}")
            return True
        except Exception as e:
            self.logger.error(f"Error setting channel: {e}")
            return False
    
    def get_adapter(self, interface: str) -> Optional[WirelessAdapter]:
        """Get adapter by interface name."""
        return self.adapters.get(interface)
    
    def get_monitor_adapters(self) -> List[WirelessAdapter]:
        """Get all adapters in monitor mode."""
        return [adapter for adapter in self.adapters.values() if adapter.is_monitor]
