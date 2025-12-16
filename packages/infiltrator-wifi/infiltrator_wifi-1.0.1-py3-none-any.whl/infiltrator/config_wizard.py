#!/usr/bin/env python3
"""
Configuration wizard for Infiltrator.
Console script: infiltrator-config
"""

import sys
from pathlib import Path
from infiltrator.core.config import Config
from infiltrator.core.banner import display_banner
from colorama import Fore, Style, init

init(autoreset=True)

def main():
    """Run configuration wizard."""
    display_banner()
    
    print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════════════════════╗")
    print(f"║          INFILTRATOR CONFIGURATION WIZARD             ║")
    print(f"╚═══════════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")
    
    config = Config()
    
    print(f"{Fore.YELLOW}Current configuration location:{Style.RESET_ALL}")
    print(f"  {config.config_file}\n")
    
    # Attack settings
    print(f"{Fore.GREEN}[1/5] Attack Settings{Style.RESET_ALL}")
    deauth_count = input(f"  Deauth count (0=continuous) [{config.get('attacks', 'deauth_count')}]: ").strip()
    if deauth_count:
        config.set('attacks', 'deauth_count', value=int(deauth_count))
    
    handshake_timeout = input(f"  Handshake timeout in seconds [{config.get('attacks', 'handshake_timeout')}]: ").strip()
    if handshake_timeout:
        config.set('attacks', 'handshake_timeout', value=int(handshake_timeout))
    
    # Stealth settings
    print(f"\n{Fore.GREEN}[2/5] Stealth Settings{Style.RESET_ALL}")
    mac_random = input(f"  Enable MAC randomization? (y/n) [y]: ").strip().lower() or 'y'
    config.set('stealth', 'mac_randomization', value=mac_random == 'y')
    
    channel_hop = input(f"  Enable channel hopping? (y/n) [y]: ").strip().lower() or 'y'
    config.set('stealth', 'channel_hopping', value=channel_hop == 'y')
    
    # Cracking settings
    print(f"\n{Fore.GREEN}[3/5] Cracking Settings{Style.RESET_ALL}")
    wordlist = input(f"  Default wordlist path [{config.get('cracking', 'default_wordlist')}]: ").strip()
    if wordlist:
        config.set('cracking', 'default_wordlist', value=wordlist)
    
    hashcat_path = input(f"  Hashcat path [{config.get('cracking', 'hashcat_path')}]: ").strip()
    if hashcat_path:
        config.set('cracking', 'hashcat_path', value=hashcat_path)
    
    # Cloud settings
    print(f"\n{Fore.GREEN}[4/5] Cloud Cracking API (Optional){Style.RESET_ALL}")
    cloud_enable = input(f"  Enable cloud cracking? (y/n) [n]: ").strip().lower() or 'n'
    config.set('cloud', 'enabled', value=cloud_enable == 'y')
    
    if cloud_enable == 'y':
        endpoint = input(f"  API endpoint URL: ").strip()
        api_key = input(f"  API key: ").strip()
        config.set('cloud', 'api_endpoint', value=endpoint)
        config.set('cloud', 'api_key', value=api_key)
    
    # GPS settings
    print(f"\n{Fore.GREEN}[5/5] GPS Settings (Optional){Style.RESET_ALL}")
    gps_enable = input(f"  Enable GPS? (y/n) [n]: ").strip().lower() or 'n'
    config.set('gps', 'enabled', value=gps_enable == 'y')
    
    if gps_enable == 'y':
        gps_device = input(f"  GPS device [{config.get('gps', 'device')}]: ").strip()
        if gps_device:
            config.set('gps', 'device', value=gps_device)
    
    # Save and display
    print(f"\n{Fore.YELLOW}Saving configuration...{Style.RESET_ALL}")
    config.ensure_directories()
    
    print(f"{Fore.GREEN}✅ Configuration saved successfully!{Style.RESET_ALL}")
    print(f"\nConfiguration file: {config.config_file}")
    print(f"\nYou can now run: {Fore.CYAN}sudo infiltrator{Style.RESET_ALL}\n")

if __name__ == "__main__":
    main()
