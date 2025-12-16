"""
Command-line interface with menu-based navigation.
"""

from colorama import Fore, Style
from typing import Optional
import sys

class CLI:
    """Main CLI interface for Infiltrator."""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.running = True
        
        # Import adapter manager
        from infiltrator.core.adapter_manager import AdapterManager
        self.adapter_manager = AdapterManager(logger)
        
        # Import module managers - lazy import to avoid circular dependencies
        try:
            from infiltrator.modules.reconnaissance import ReconnaissanceModule
            from infiltrator.modules.exploitation import ExploitationModule
            from infiltrator.modules.post_attack import PostAttackModule
            
            self.recon_module = ReconnaissanceModule(config, logger, self.adapter_manager)
            self.exploit_module = ExploitationModule(config, logger, self.adapter_manager)
            self.post_module = PostAttackModule(config, logger, self.adapter_manager)
        except ImportError as e:
            self.logger.warning(f"Some modules could not be loaded: {e}")
            self.logger.info("Basic functionality will still be available")
        
        # Ensure directories exist
        self.config.ensure_directories()
    
    def run(self):
        """Main CLI loop."""
        # Initial setup
        self._setup_adapters()
        
        while self.running:
            self._display_main_menu()
            choice = self._get_input("Select option")
            
            if choice == '1':
                self._reconnaissance_menu()
            elif choice == '2':
                self._exploitation_menu()
            elif choice == '3':
                self._post_attack_menu()
            elif choice == '4':
                self._adapter_menu()
            elif choice == '5':
                self._settings_menu()
            elif choice == '0':
                self._exit()
            else:
                self.logger.error("Invalid option. Please try again.")
    
    def _setup_adapters(self):
        """Initial adapter setup."""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("ADAPTER INITIALIZATION")
        self.logger.info("=" * 60)
        
        adapters = self.adapter_manager.scan_adapters()
        
        if not adapters:
            self.logger.error("No wireless adapters found!")
            self.logger.warning("Please connect a wireless adapter and restart.")
            self.logger.info("You can still explore settings and documentation.")
            return
        
        # Display found adapters
        print(f"\n{Fore.CYAN}Available Adapters:{Style.RESET_ALL}")
        for i, adapter in enumerate(adapters, 1):
            print(f"  [{i}] {adapter.interface} - {adapter.driver} - {adapter.mac_address} - Mode: {adapter.mode}")
        
        # Ask to enable monitor mode
        print(f"\n{Fore.YELLOW}Monitor mode is required for most attacks{Style.RESET_ALL}")
        choice = self._get_input("Enable monitor mode on all adapters? (y/n)", default="y")
        
        if choice.lower() == 'y':
            for adapter in adapters:
                if not adapter.is_monitor:
                    self.adapter_manager.enable_monitor_mode(adapter.interface)
    
    def _display_main_menu(self):
        """Display main menu."""
        print(f"\n{Fore.CYAN}╔════════════════════════════════════════════════════════════╗")
        print(f"║                        MAIN MENU                           ║")
        print(f"╚════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        print(f"\n{Fore.GREEN}[1]{Style.RESET_ALL} Reconnaissance & Intelligence Gathering")
        print(f"{Fore.GREEN}[2]{Style.RESET_ALL} Exploitation & Attack Automation")
        print(f"{Fore.GREEN}[3]{Style.RESET_ALL} Post-Attack Operations & Management")
        print(f"{Fore.GREEN}[4]{Style.RESET_ALL} Adapter Management")
        print(f"{Fore.GREEN}[5]{Style.RESET_ALL} Settings & Configuration")
        print(f"{Fore.RED}[0]{Style.RESET_ALL} Exit")
        print()
    
    def _reconnaissance_menu(self):
        """Reconnaissance submenu."""
        if not hasattr(self, 'recon_module'):
            self.logger.error("Reconnaissance module not available")
            return
        
        while True:
            print(f"\n{Fore.CYAN}╔════════════════════════════════════════════════════════════╗")
            print(f"║                RECONNAISSANCE & INTELLIGENCE               ║")
            print(f"╚════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
            print(f"\n{Fore.GREEN}[1]{Style.RESET_ALL} Passive Scanner & Analyzer")
            print(f"{Fore.GREEN}[2]{Style.RESET_ALL} Client Probe Monitor")
            print(f"{Fore.GREEN}[3]{Style.RESET_ALL} Target Tracker")
            print(f"{Fore.GREEN}[4]{Style.RESET_ALL} Geo-Spatial Mapper (War-Driving)")
            print(f"{Fore.GREEN}[5]{Style.RESET_ALL} Protocol Fingerprinter")
            print(f"{Fore.YELLOW}[0]{Style.RESET_ALL} Back to Main Menu")
            print()
            
            choice = self._get_input("Select option")
            
            if choice == '1':
                self.recon_module.passive_scanner()
            elif choice == '2':
                self.recon_module.client_probe_monitor()
            elif choice == '3':
                self.recon_module.target_tracker()
            elif choice == '4':
                self.recon_module.geo_mapper()
            elif choice == '5':
                self.recon_module.protocol_fingerprinter()
            elif choice == '0':
                break
            else:
                self.logger.error("Invalid option")
    
    def _exploitation_menu(self):
        """Exploitation submenu."""
        if not hasattr(self, 'exploit_module'):
            self.logger.error("Exploitation module not available")
            return
        
        while True:
            print(f"\n{Fore.CYAN}╔════════════════════════════════════════════════════════════╗")
            print(f"║               EXPLOITATION & ATTACK AUTOMATION             ║")
            print(f"╚════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
            print(f"\n{Fore.GREEN}[1]{Style.RESET_ALL} Deauth Attack Suite")
            print(f"{Fore.GREEN}[2]{Style.RESET_ALL} Handshake/PMKID Capture")
            print(f"{Fore.GREEN}[3]{Style.RESET_ALL} Multi-Adapter Evil Twin (MiTM)")
            print(f"{Fore.GREEN}[4]{Style.RESET_ALL} WPS Brute-Forcer")
            print(f"{Fore.GREEN}[5]{Style.RESET_ALL} WPA3-SAE Downgrade Attack")
            print(f"{Fore.GREEN}[6]{Style.RESET_ALL} 802.1X EAP Phishing Suite")
            print(f"{Fore.YELLOW}[0]{Style.RESET_ALL} Back to Main Menu")
            print()
            
            choice = self._get_input("Select option")
            
            if choice == '1':
                self.exploit_module.deauth_attack()
            elif choice == '2':
                self.exploit_module.handshake_capture()
            elif choice == '3':
                self.exploit_module.evil_twin()
            elif choice == '4':
                self.exploit_module.wps_attack()
            elif choice == '5':
                self.exploit_module.wpa3_downgrade()
            elif choice == '6':
                self.exploit_module.eap_phishing()
            elif choice == '0':
                break
            else:
                self.logger.error("Invalid option")
    
    def _post_attack_menu(self):
        """Post-attack operations submenu."""
        if not hasattr(self, 'post_module'):
            self.logger.error("Post-attack module not available")
            return
        
        while True:
            print(f"\n{Fore.CYAN}╔════════════════════════════════════════════════════════════╗")
            print(f"║            POST-ATTACK OPERATIONS & MANAGEMENT             ║")
            print(f"╚════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
            print(f"\n{Fore.GREEN}[1]{Style.RESET_ALL} Offline Cracking Integration")
            print(f"{Fore.GREEN}[2]{Style.RESET_ALL} Automated Chain Execution")
            print(f"{Fore.GREEN}[3]{Style.RESET_ALL} Stealth & OPSEC Tools")
            print(f"{Fore.GREEN}[4]{Style.RESET_ALL} Cloud Cracking API")
            print(f"{Fore.YELLOW}[0]{Style.RESET_ALL} Back to Main Menu")
            print()
            
            choice = self._get_input("Select option")
            
            if choice == '1':
                self.post_module.offline_cracking()
            elif choice == '2':
                self.post_module.chain_execution()
            elif choice == '3':
                self.post_module.stealth_opsec()
            elif choice == '4':
                self.post_module.cloud_cracking()
            elif choice == '0':
                break
            else:
                self.logger.error("Invalid option")
    
    def _adapter_menu(self):
        """Adapter management submenu."""
        while True:
            print(f"\n{Fore.CYAN}╔════════════════════════════════════════════════════════════╗")
            print(f"║                    ADAPTER MANAGEMENT                      ║")
            print(f"╚════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
            
            adapters = list(self.adapter_manager.adapters.values())
            if adapters:
                print(f"\n{Fore.YELLOW}Current Adapters:{Style.RESET_ALL}")
                for i, adapter in enumerate(adapters, 1):
                    status = f"{Fore.GREEN}MONITOR{Style.RESET_ALL}" if adapter.is_monitor else f"{Fore.RED}MANAGED{Style.RESET_ALL}"
                    print(f"  [{i}] {adapter.interface} - {adapter.driver} - {adapter.mac_address}")
                    print(f"      Mode: {status} | Channel: {adapter.channel if adapter.channel else 'N/A'}")
            
            print(f"\n{Fore.GREEN}[1]{Style.RESET_ALL} Rescan Adapters")
            print(f"{Fore.GREEN}[2]{Style.RESET_ALL} Enable Monitor Mode")
            print(f"{Fore.GREEN}[3]{Style.RESET_ALL} Disable Monitor Mode")
            print(f"{Fore.GREEN}[4]{Style.RESET_ALL} Spoof MAC Address")
            print(f"{Fore.GREEN}[5]{Style.RESET_ALL} Restore MAC Address")
            print(f"{Fore.GREEN}[6]{Style.RESET_ALL} Set Channel")
            print(f"{Fore.YELLOW}[0]{Style.RESET_ALL} Back to Main Menu")
            print()
            
            choice = self._get_input("Select option")
            
            if choice == '1':
                self.adapter_manager.scan_adapters()
            elif choice == '2':
                interface = self._get_input("Interface name")
                self.adapter_manager.enable_monitor_mode(interface)
            elif choice == '3':
                interface = self._get_input("Interface name")
                self.adapter_manager.disable_monitor_mode(interface)
            elif choice == '4':
                interface = self._get_input("Interface name")
                self.adapter_manager.spoof_mac(interface)
            elif choice == '5':
                interface = self._get_input("Interface name")
                self.adapter_manager.restore_mac(interface)
            elif choice == '6':
                interface = self._get_input("Interface name")
                channel = int(self._get_input("Channel number"))
                self.adapter_manager.set_channel(interface, channel)
            elif choice == '0':
                break
            else:
                self.logger.error("Invalid option")
    
    def _settings_menu(self):
        """Settings submenu."""
        while True:
            print(f"\n{Fore.CYAN}╔════════════════════════════════════════════════════════════╗")
            print(f"║                 SETTINGS & CONFIGURATION                   ║")
            print(f"╚════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
            print(f"\n{Fore.GREEN}[1]{Style.RESET_ALL} View Current Config")
            print(f"{Fore.GREEN}[2]{Style.RESET_ALL} Run Configuration Wizard")
            print(f"{Fore.YELLOW}[0]{Style.RESET_ALL} Back to Main Menu")
            print()
            
            choice = self._get_input("Select option")
            
            if choice == '1':
                self._view_config()
            elif choice == '2':
                self.logger.info("Run: infiltrator-config")
            elif choice == '0':
                break
            else:
                self.logger.error("Invalid option")
    
    def _view_config(self):
        """Display current configuration."""
        print(f"\n{Fore.YELLOW}Current Configuration:{Style.RESET_ALL}")
        import json
        print(json.dumps(self.config.config, indent=2))
    
    def _get_input(self, prompt: str, default: str = None) -> str:
        if default:
            prompt = f"{Fore.YELLOW}[?]{Style.RESET_ALL} {prompt} [{default}]: "
        else:
            prompt = f"{Fore.YELLOW}[?]{Style.RESET_ALL} {prompt}: "
        
        user_input = input(prompt).strip()
        return user_input if user_input else (default if default else "")
    
    def _exit(self):
        """Exit the application."""
        print(f"\n{Fore.YELLOW}Cleaning up...{Style.RESET_ALL}")
        self.cleanup()
        self.logger.info("Goodbye!")
        self.running = False
    
    def cleanup(self):
        """Cleanup operations."""
        for interface in self.adapter_manager.monitor_adapters[:]:
            self.adapter_manager.disable_monitor_mode(interface)
        
        for adapter in self.adapter_manager.adapters.values():
            if adapter.mac_address != adapter.original_mac:
                self.adapter_manager.restore_mac(adapter.interface)
