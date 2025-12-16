"""
ARTC-LITE:  Lightweight IoT Tensor Encoding

Optimized for: 
- IoT sensors (temperature, pressure, humidity)
- Battery-powered devices
- Slow wireless (LoRa, Bluetooth, Zigbee)
- Microcontrollers (Arduino, ESP32, Raspberry Pi)

Design principles:
- Minimal memory footprint
- Fast compression/decompression
- Simple linear regression only (no complex math)
- Easy to port to C/Arduino
"""

import numpy as np
from typing import List, Dict, Union


class ARTCLITE:
    """
    ARTC-LITE: Lightweight IoT Tensor Encoding
    
    Designed for resource-constrained IoT devices. 
    
    Args:
        block_size: Number of values per block (default: 8, smaller = less RAM)
        tolerance: Maximum acceptable error (default: 0.1)
        
    Example - Temperature Sensor:
        >>> from artc import ARTCLITE
        >>> import numpy as np
        >>> 
        >>> # Simulated temperature readings
        >>> temps = np.array([20.1, 20.2, 20.3, 20.4, 20.5, 20.6, 20.7, 20.8])
        >>> 
        >>> # Compress for transmission
        >>> compressor = ARTCLITE(block_size=8, tolerance=0.1)
        >>> compressed = compressor.compress(temps)
        >>> 
        >>> # Shows compression stats
        >>> compressor.print_stats()
        >>> 
        >>> # Decompress on receiver side
        >>> decompressed = compressor.decompress(compressed)
    
    Example - Streaming Mode (for real-time sensors):
        >>> compressor = ARTCLITE(block_size=8)
        >>> 
        >>> # Add readings as they come in
        >>> for reading in sensor_stream:
        >>>     compressor.add_reading(reading)
        >>>     
        >>>     # When block is full, get compressed output
        >>>     if compressor.block_ready():
        >>>         compressed = compressor.get_block()
        >>>         send_via_lora(compressed)  # Send over LoRa
    """
    
    def __init__(self, block_size: int = 8, tolerance: float = 0.1):
        self.block_size = block_size
        self.tolerance = tolerance
        
        # Stats
        self.stats = {
            'original_size': 0,
            'compressed_size': 0,
            'blocks_compressed': 0,
            'blocks_raw': 0,
            'total_readings': 0
        }
        
        # Streaming mode buffer
        self._buffer = []
    
    def compress(self, data: Union[np.ndarray, List[float]]) -> List[Dict]:
        """
        Compress sensor data in batch mode.
        
        Args:
            data: Array or list of sensor readings
            
        Returns: 
            List of compressed blocks (ready to serialize/transmit)
        """
        if isinstance(data, list):
            data = np.array(data, dtype=np.float32)
        else:
            data = np.asarray(data, dtype=np.float32)
        
        self.stats['original_size'] = data.nbytes
        self.stats['total_readings'] = len(data)
        
        compressed_blocks = []
        compressed_size = 0
        blocks_compressed = 0
        blocks_raw = 0
        
        # Process each block
        for i in range(0, len(data), self.block_size):
            block = data[i:i+self.block_size]
            
            # Skip incomplete blocks
            if len(block) < self.block_size:
                continue
            
            # Try linear fit:   y = mx + b
            compressed_block, block_type = self._compress_block(block)
            compressed_blocks.append(compressed_block)
            
            # Update stats
            if block_type == 'formula': 
                compressed_size += 8  # m (4 bytes) + b (4 bytes)
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
        Decompress back to original readings.
        
        Args:
            compressed_blocks: Output from compress()
            
        Returns:
            Reconstructed sensor readings
        """
        reconstructed = []
        
        for block in compressed_blocks:
            if block['type'] == 'formula':
                # Rebuild from formula
                x = np.arange(self.block_size, dtype=np.float32)
                values = block['m'] * x + block['b']
                reconstructed.extend(values)
            else:
                # Copy raw data
                reconstructed.extend(block['data'])
        
        return np.array(reconstructed, dtype=np.float32)
    
    def _compress_block(self, block: np.ndarray) -> tuple:
        """
        Compress a single block using simple linear regression.
        
        Returns:
            (compressed_dict, block_type)
        """
        n = len(block)
        
        # Indices:  0, 1, 2, ..., n-1
        x = np.arange(n, dtype=np.float32)
        
        # Simple linear fit:   y = mx + b
        # Using the least squares formulas
        x_mean = x.mean()
        y_mean = block.mean()
        
        numerator = np.sum((x - x_mean) * (block - y_mean))
        denominator = np.sum((x - x_mean) ** 2)
        
        if denominator < 1e-10:
            # All x values same (shouldn't happen) - treat as constant
            m = 0.0
            b = y_mean
        else:
            m = numerator / denominator
            b = y_mean - m * x_mean
        
        # Calculate error
        predicted = m * x + b
        residuals = block - predicted
        max_error = np.max(np.abs(residuals))
        
        if max_error <= self.tolerance:
            # Good fit! 
            return {
                'type': 'formula',
                'm': float(m),
                'b': float(b)
            }, 'formula'
        else:
            # Bad fit, store raw
            return {
                'type': 'raw',
                'data': block.tolist()
            }, 'raw'
    
    # ========================================================================
    # STREAMING MODE (for real-time sensor data)
    # ========================================================================
    
    def add_reading(self, value: float):
        """
        Add a single sensor reading (streaming mode).
        
        Args:
            value: Single sensor reading
            
        Example:
            >>> compressor = ARTCLITE(block_size=8)
            >>> for temp in sensor.read_stream():
            >>>     compressor.add_reading(temp)
            >>>     if compressor.block_ready():
            >>>         compressed = compressor.get_block()
            >>>         send_over_network(compressed)
        """
        self._buffer.append(float(value))
        self.stats['total_readings'] += 1
    
    def block_ready(self) -> bool:
        """Check if buffer has a complete block ready."""
        return len(self._buffer) >= self.block_size
    
    def get_block(self) -> Dict:
        """
        Get compressed block from buffer (streaming mode).
        
        Returns:
            Single compressed block, or None if not ready
        """
        if not self.block_ready():
            return None
        
        # Extract one block
        block_data = np.array(self._buffer[:self.block_size], dtype=np.float32)
        self._buffer = self._buffer[self.block_size:]
        
        # Compress it
        compressed_block, block_type = self._compress_block(block_data)
        
        # Update stats
        if block_type == 'formula':
            self.stats['compressed_size'] += 8
            self.stats['blocks_compressed'] += 1
        else: 
            self.stats['compressed_size'] += len(block_data) * 4
            self.stats['blocks_raw'] += 1
        
        self.stats['original_size'] += len(block_data) * 4
        
        return compressed_block
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def get_ratio(self) -> float:
        """Get compression ratio."""
        if self.stats['compressed_size'] == 0:
            return 1.0
        return self.stats['original_size'] / self.stats['compressed_size']
    
    def print_stats(self):
        """Print compression statistics."""
        print("=" * 50)
        print("ARTC-LITE Compression Stats")
        print("=" * 50)
        print(f"Total readings:     {self.stats['total_readings']}")
        print(f"Original size:      {self.stats['original_size']} bytes")
        print(f"Compressed size:    {self.stats['compressed_size']} bytes")
        print(f"Compression ratio:  {self.get_ratio():.1f}x smaller")
        print(f"Blocks compressed:  {self.stats['blocks_compressed']}")
        print(f"Blocks raw:         {self.stats['blocks_raw']}")
        
        if self.stats['blocks_compressed'] + self.stats['blocks_raw'] > 0:
            success_rate = 100 * self.stats['blocks_compressed'] / (
                self.stats['blocks_compressed'] + self.stats['blocks_raw']
            )
            print(f"Success rate:       {success_rate:.0f}%")
        print("=" * 50)
    
    def reset_stats(self):
        """Reset statistics (useful for streaming)."""
        self.stats = {
            'original_size': 0,
            'compressed_size': 0,
            'blocks_compressed': 0,
            'blocks_raw': 0,
            'total_readings': 0
        }
    
    def clear_buffer(self):
        """Clear streaming buffer."""
        self._buffer = []
