"""
ARTC - Adaptive Regression Tensor Compression
A family of compression algorithms for different use cases

Variants:
- ARTC: Base algorithm
- ARTC-LITE:  Lightweight IoT Tensor Encoding (for sensors, embedded)
- ARTC-VRAM: GPU memory compression (coming soon)
- ARTC-IO: Transfer compression (coming soon)
"""

from .core import ARTC
from .lite import ARTCLITE

__version__ = "0.1.0"
__all__ = ["ARTC", "ARTCLITE"]
