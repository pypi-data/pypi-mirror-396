"""
Infiltrator WiFi Red Team Auditing Suite
Developer: LAKSHMIKANTHAN K (letchupkt)

A comprehensive, modular WiFi penetration testing framework for educational
and authorized security testing purposes only.
"""

__version__ = '1.0.1'
__author__ = 'LAKSHMIKANTHAN K'
__email__ = 'letchupkt@example.com'
__license__ = 'MIT'

from infiltrator.core.config import Config
from infiltrator.core.logger import Logger

__all__ = ['Config', 'Logger', '__version__']
