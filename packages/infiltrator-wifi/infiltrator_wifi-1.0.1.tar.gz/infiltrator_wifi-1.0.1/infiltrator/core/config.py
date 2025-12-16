"""Configuration management for Infiltrator."""

import json
import os
from pathlib import Path
from typing import Any, Dict

class Config:
    """Manages configuration settings for Infiltrator."""
    
    def __init__(self, config_file: str = None):
        self.config_dir = Path.home() / '.infiltrator'
        self.config_dir.mkdir(exist_ok=True)
        
        if config_file is None:
            config_file = self.config_dir / 'config.json'
        
        self.config_file = Path(config_file)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return self._default_config()
        else:
            config = self._default_config()
            self.save()
            return config
    
    def _default_config(self) -> Dict[str, Any]:
        return {
            'adapters': {'monitor_mode_adapters': [], 'primary_adapter': None, 'secondary_adapter': None},
            'output': {
                'captures_dir': str(self.config_dir / 'captures'),
                'logs_dir': str(self.config_dir / 'logs'),
                'wordlists_dir': str(self.config_dir / 'wordlists')
            },
            'attacks': {'deauth_count': 0, 'deauth_delay': 0.1, 'handshake_timeout': 120, 'evil_twin_channel': 6, 'wps_timeout': 300},
            'stealth': {'mac_randomization': True, 'random_ssid': True, 'channel_hopping': True, 'hop_interval': 0.5},
            'cracking': {'hashcat_path': 'hashcat', 'john_path': 'john', 'default_wordlist': '/usr/share/wordlists/rockyou.txt', 'rules_file': None},
            'cloud': {'enabled': False, 'api_endpoint': None, 'api_key': None},
            'gps': {'enabled': False, 'device': '/dev/ttyUSB0', 'baud_rate': 9600}
        }
    
    def save(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def get(self, *keys, default=None) -> Any:
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def set(self, *keys, value):
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        self.save()
    
    def ensure_directories(self):
        Path(self.get('output', 'captures_dir')).mkdir(parents=True, exist_ok=True)
        Path(self.get('output', 'logs_dir')).mkdir(parents=True, exist_ok=True)
        Path(self.get('output', 'wordlists_dir')).mkdir(parents=True, exist_ok=True)
