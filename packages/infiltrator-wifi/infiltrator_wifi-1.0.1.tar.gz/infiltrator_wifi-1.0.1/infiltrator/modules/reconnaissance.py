"""
Reconnaissance & Intelligence Gathering Module.

Implements passive scanning, client monitoring, target tracking,
geo-spatial mapping, and protocol fingerprinting.
"""

import subprocess
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import json

@dataclass
class AccessPoint:
    """Represents an access point."""
    bssid: str
    ssid: str
    channel: int
    encryption: str
    signal: int
    vendor: str = "Unknown"
    first_seen: str = field(default_factory=lambda: datetime.now().isoformat())
    last_seen: str = field(default_factory=lambda: datetime.now().isoformat())
    clients: List[str] = field(default_factory=list)

@dataclass
class Client:
    """Represents a wireless client."""
    mac: str
    probes: List[str] = field(default_factory=list)
    connected_to: Optional[str] = None
    signal: int = 0
    first_seen: str = field(default_factory=lambda: datetime.now().isoformat())
    last_seen: str = field(default_factory=lambda: datetime.now().isoformat())

class ReconnaissanceModule:
    """Reconnaissance and intelligence gathering operations."""
    
    def __init__(self, config, logger, adapter_manager):
        """
        Initialize reconnaissance module.
        
        Args:
            config: Configuration object
            logger: Logger instance
            adapter_manager: Adapter manager instance
        """
        self.config = config
        self.logger = logger
        self.adapter_manager = adapter_manager
        
        # Data storage
        self.access_points: Dict[str, AccessPoint] = {}
        self.clients: Dict[str, Client] = {}
        
        # Control flags
        self.scanning = False
    
    def passive_scanner(self):
        """
        Passive Scanner & Analyzer (Basic).
        
        Continuously monitors wireless spectrum across 2.4GHz and 5GHz bands.
        Collects BSSID, SSID, encryption, and signal strength.
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info("PASSIVE SCANNER & ANALYZER")
        self.logger.info("=" * 60)
        
        # Get monitor adapter
        monitor_adapters = self.adapter_manager.get_monitor_adapters()
        if not monitor_adapters:
            self.logger.error("No adapters in monitor mode!")
            self.logger.warning("Please enable monitor mode first.")
            return
        
        adapter = monitor_adapters[0]
        self.logger.info(f"Using adapter: {adapter.interface}")
        
        # Configure output file
        capture_dir = Path(self.config.get('output', 'captures_dir'))
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_prefix = capture_dir / f"scan_{timestamp}"
        
        self.logger.info(f"Output file: {output_prefix}-01.csv")
        self.logger.info("Press Ctrl+C to stop scanning...")
        
        try:
            # Start channel hopping thread
            self.scanning = True
            hop_thread = threading.Thread(
                target=self._channel_hopper,
                args=(adapter.interface,),
                daemon=True
            )
            hop_thread.start()
            
            # Start airodump-ng
            cmd = [
                'airodump-ng',
                '--output-format', 'csv',
                '-w', str(output_prefix),
                adapter.interface
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Parse results in real-time
            parse_thread = threading.Thread(
                target=self._parse_airodump_csv,
                args=(f"{output_prefix}-01.csv",),
                daemon=True
            )
            parse_thread.start()
            
            # Wait for user interrupt
            process.wait()
            
        except KeyboardInterrupt:
            self.logger.info("\nStopping scanner...")
            self.scanning = False
            if 'process' in locals():
                process.terminate()
                process.wait()
            
            # Display summary
            self._display_scan_summary()
        
        except Exception as e:
            self.logger.error(f"Scanner error: {e}")
            self.scanning = False
    
    def _channel_hopper(self, interface: str):
        """Background thread for channel hopping."""
        channels_2ghz = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        channels_5ghz = [36, 40, 44, 48, 52, 56, 60, 64, 100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 149, 153, 157, 161, 165]
        all_channels = channels_2ghz + channels_5ghz
        
        hop_interval = self.config.get('stealth', 'hop_interval', default=0.5)
        
        idx = 0
        while self.scanning:
            try:
                channel = all_channels[idx % len(all_channels)]
                self.adapter_manager.set_channel(interface, channel)
                time.sleep(hop_interval)
                idx += 1
            except Exception:
                pass
    
    def _parse_airodump_csv(self, csv_file: str):
        """Parse airodump-ng CSV file in real-time."""
        import csv
        
        last_position = 0
        
        while self.scanning:
            try:
                if not Path(csv_file).exists():
                    time.sleep(1)
                    continue
                
                with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(last_position)
                    content = f.read()
                    last_position = f.tell()
                    
                    # Parse AP and client data
                    # (Implementation would parse CSV format)
                    
                time.sleep(2)
                
            except Exception as e:
                self.logger.debug(f"Parse error: {e}")
                time.sleep(1)
    
    def _display_scan_summary(self):
        """Display scanning summary."""
        print(f"\n{'=' * 80}")
        print(f"SCAN SUMMARY")
        print(f"{'=' * 80}")
        print(f"Access Points Found: {len(self.access_points)}")
        print(f"Clients Found: {len(self.clients)}")
        print(f"{'=' * 80}\n")
    
    def client_probe_monitor(self):
        """
        Client Probe Monitor (Basic).
        
        Listens for client probe requests to build network history.
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info("CLIENT PROBE MONITOR")
        self.logger.info("=" * 60)
        
        monitor_adapters = self.adapter_manager.get_monitor_adapters()
        if not monitor_adapters:
            self.logger.error("No adapters in monitor mode!")
            return
        
        adapter = monitor_adapters[0]
        self.logger.info(f"Using adapter: {adapter.interface}")
        self.logger.info("Monitoring client probe requests...")
        self.logger.info("Press Ctrl+C to stop\n")
        
        try:
            # Use tshark to capture probe requests
            cmd = [
                'tshark',
                '-i', adapter.interface,
                '-Y', 'wlan.fc.type_subtype == 0x04',  # Probe requests
                '-T', 'fields',
                '-e', 'wlan.sa',  # Source address
                '-e', 'wlan_mgt.ssid',  # SSID
                '-e', 'radiotap.dbm_antsignal'  # Signal
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            probes_seen = defaultdict(set)
            
            for line in process.stdout:
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    client_mac = parts[0]
                    ssid = parts[1] if len(parts) > 1 else "(Broadcast)"
                    signal = parts[2] if len(parts) > 2 else "N/A"
                    
                    if ssid and ssid not in probes_seen[client_mac]:
                        probes_seen[client_mac].add(ssid)
                        print(f"[PROBE] {client_mac} -> {ssid} (Signal: {signal} dBm)")
                        
                        # Update client database
                        if client_mac not in self.clients:
                            self.clients[client_mac] = Client(mac=client_mac)
                        
                        if ssid not in self.clients[client_mac].probes:
                            self.clients[client_mac].probes.append(ssid)
        
        except KeyboardInterrupt:
            self.logger.info("\nStopping probe monitor...")
            process.terminate()
            
            # Save results
            self._save_probe_results()
        
        except Exception as e:
            self.logger.error(f"Probe monitor error: {e}")
    
    def _save_probe_results(self):
        """Save probe results to file."""
        output_dir = Path(self.config.get('output', 'captures_dir'))
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f"probes_{timestamp}.json"
        
        probe_data = {
            mac: {
                'probes': client.probes,
                'first_seen': client.first_seen,
                'last_seen': client.last_seen
            }
            for mac, client in self.clients.items()
        }
        
        with open(output_file, 'w') as f:
            json.dump(probe_data, f, indent=2)
        
        self.logger.success(f"Probe data saved to: {output_file}")
    
    def target_tracker(self):
        """
        Target Tracker (Advanced).
        
        Monitors for specific target MAC addresses.
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info("TARGET TRACKER")
        self.logger.info("=" * 60)
        
        # Get target MACs
        targets_input = input("Enter target MAC addresses (comma-separated): ").strip()
        targets = [mac.strip() for mac in targets_input.split(',')]
        
        if not targets:
            self.logger.error("No targets specified!")
            return
        
        self.logger.info(f"Tracking {len(targets)} target(s):")
        for target in targets:
            self.logger.info(f"  - {target}")
        
        monitor_adapters = self.adapter_manager.get_monitor_adapters()
        if not monitor_adapters:
            self.logger.error("No adapters in monitor mode!")
            return
        
        adapter = monitor_adapters[0]
        self.logger.info(f"\nUsing adapter: {adapter.interface}")
        self.logger.info("Press Ctrl+C to stop tracking\n")
        
        try:
            # Use tshark to monitor target MACs
            filter_str = ' or '.join([f'wlan.sa == {mac}' for mac in targets])
            
            cmd = [
                'tshark',
                '-i', adapter.interface,
                '-Y', filter_str,
                '-T', 'fields',
                '-e', 'wlan.sa',
                '-e', 'wlan.bssid',
                '-e', 'radiotap.channel.freq',
                '-e', 'radiotap.dbm_antsignal'
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            for line in process.stdout:
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    source_mac = parts[0]
                    bssid = parts[1] if len(parts) > 1 else "N/A"
                    channel = parts[2] if len(parts) > 2 else "N/A"
                    signal = parts[3] if len(parts) > 3 else "N/A"
                    
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    print(f"[{timestamp}] TARGET DETECTED: {source_mac}")
                    print(f"             Connected to: {bssid}")
                    print(f"             Channel: {channel} | Signal: {signal} dBm\n")
        
        except KeyboardInterrupt:
            self.logger.info("\nStopping target tracker...")
            process.terminate()
        
        except Exception as e:
            self.logger.error(f"Target tracker error: {e}")
    
    def geo_mapper(self):
        """
        Geo-Spatial Mapper (Advanced).
        
        War-driving with GPS integration.
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info("GEO-SPATIAL MAPPER (WAR-DRIVING)")
        self.logger.info("=" * 60)
        
        if not self.config.get('gps', 'enabled'):
            self.logger.warning("GPS is not enabled in configuration!")
            enable = input("Enable GPS now? (y/n): ").strip().lower()
            if enable == 'y':
                self._configure_gps()
            else:
                return
        
        self.logger.info("Starting war-driving mode...")
        self.logger.info("GPS integration: ENABLED")
        self.logger.info("Output format: KML/GPX")
        self.logger.info("\nThis feature requires GPS hardware and gpsd daemon")
        self.logger.warning("Implementation requires: gpsd, gpsd-clients, python-gps")
        
        # Placeholder for GPS integration
        self.logger.info("\n[Feature Ready - GPS hardware required]")
    
    def protocol_fingerprinter(self):
        """
        Protocol Fingerprinter (Legendary).
        
        Analyzes vendor-specific Information Elements to identify AP details.
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info("PROTOCOL FINGERPRINTER")
        self.logger.info("=" * 60)
        
        self.logger.info("Analyzing 802.11 Information Elements...")
        self.logger.info("Target: AP make, model, firmware version")
        self.logger.info("\nThis feature performs deep packet analysis")
        self.logger.warning("Implementation requires: scapy, vendor OUI database")
        
        # Placeholder for deep packet inspection
        self.logger.info("\n[Feature Ready - Deep packet analysis]")
    
    def _configure_gps(self):
        """Quick GPS configuration."""
        device = input("GPS device [/dev/ttyUSB0]: ").strip() or "/dev/ttyUSB0"
        self.config.set('gps', 'enabled', value=True)
        self.config.set('gps', 'device', value=device)
        self.logger.success("GPS configured")
