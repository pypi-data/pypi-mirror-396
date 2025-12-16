"""
Sarmadtec NeuroPort device driver.

Public API:
    - Device: main driver class for Fascin8/Ultim8 devices or faker mode.
"""

from .device import Device

__all__ = ["Device"]
__version__ = "0.2.0"
