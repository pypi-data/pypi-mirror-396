"""
ARTC - Adaptive Regression Tensor Compression
Base algorithm implementation
"""

import numpy as np
from typing import List, Dict, Union


class ARTC:
    """
    ARTC: Adaptive Regression Tensor Compression
    
    Base compression algorithm using regression-based tensor encoding.
    
    Args:
        block_size: Number of values per block (default: 16)
        tolerance: Maximum acceptable error (default: 0.1)
    """
    
    def __init__(self, block_size: int = 16, tolerance: float = 0.1):
        self.block_size = block_size
        self.tolerance = tolerance
        
        self.stats = {
            'original_size': 0,
            'compressed_size': 0,
            'blocks_compressed': 0,
            'blocks_raw': 0,
            'total_values': 0
        }
    
    def compress(self, data: Union[np.ndarray, List[float]]) -> List[Dict]:
        """
        Compress data using adaptive regression.
        
        Args:
            data: Array or list of values
            
        Returns:
            List of compressed blocks
        """
        if isinstance(data, list):
            data = np.array(data, dtype=np.float32)
        else:
            data = np.asarray(data, dtype=np.float32)
        
        self.stats['original_size'] = data.nbytes
        self.stats['total_values'] = len(data)
        
        compressed_blocks = []
        compressed_size = 0
        blocks_compressed = 0
        blocks_raw = 0
        
        for i in range(0, len(data), self.block_size):
            block = data[i:i+self.block_size]
            
            if len(block) < self.block_size:
                continue
            
            compressed_block, block_type = self._compress_block(block)
            compressed_blocks.append(compressed_block)
            
            if block_type == 'formula':
                compressed_size += 8
                blocks_compressed += 1
            else:
                compressed_size += len(block) * 4
                blocks_raw += 1
        
        self.stats['compressed_size'] = compressed_size
        self.stats['blocks_compressed'] = blocks_compressed
        self.stats['blocks_raw'] = blocks_raw
        
        return compressed_blocks
    
    def decompress(self, compressed_blocks: List[Dict]) -> np.ndarray:
        """
        Decompress back to original data.
        
        Args:
            compressed_blocks: Output from compress()
            
        Returns:
            Reconstructed data
        """
        reconstructed = []
        
        for block in compressed_blocks:
            if block['type'] == 'formula':
                x = np.arange(self.block_size, dtype=np.float32)
                values = block['m'] * x + block['b']
                reconstructed.extend(values)
            else:
                reconstructed.extend(block['data'])
        
        return np.array(reconstructed, dtype=np.float32)
    
    def _compress_block(self, block: np.ndarray) -> tuple:
        """
        Compress a single block using linear regression.
        """
        n = len(block)
        x = np.arange(n, dtype=np.float32)
        
        x_mean = x.mean()
        y_mean = block.mean()
        
        numerator = np.sum((x - x_mean) * (block - y_mean))
        denominator = np.sum((x - x_mean) ** 2)
        
        if denominator < 1e-10:
            m = 0.0
            b = y_mean
        else:
            m = numerator / denominator
            b = y_mean - m * x_mean
        
        predicted = m * x + b
        residuals = block - predicted
        max_error = np.max(np.abs(residuals))
        
        if max_error <= self.tolerance:
            return {
                'type': 'formula',
                'm': float(m),
                'b': float(b)
            }, 'formula'
        else:
            return {
                'type': 'raw',
                'data': block.tolist()
            }, 'raw'
    
    def get_ratio(self) -> float:
        """Get compression ratio."""
        if self.stats['compressed_size'] == 0:
            return 1.0
        return self.stats['original_size'] / self.stats['compressed_size']
    
    def print_stats(self):
        """Print compression statistics."""
        print("=" * 50)
        print("ARTC Compression Stats")
        print("=" * 50)
        print(f"Total values:       {self.stats['total_values']}")
        print(f"Original size:      {self.stats['original_size']} bytes")
        print(f"Compressed size:    {self.stats['compressed_size']} bytes")
        print(f"Compression ratio:  {self.get_ratio():.1f}x smaller")
        print(f"Blocks compressed:  {self.stats['blocks_compressed']}")
        print(f"Blocks raw:         {self.stats['blocks_raw']}")
        print("=" * 50)
