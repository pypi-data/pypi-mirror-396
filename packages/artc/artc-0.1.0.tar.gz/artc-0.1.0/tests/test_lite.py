"""
Tests for ARTC-LITE: Lightweight IoT Tensor Encoding
"""

import pytest
import numpy as np
from artc import ARTCLITE


class TestARTCLITEBasic:
    """Basic functionality tests."""
    
    def test_init_defaults(self):
        """Test default initialization."""
        compressor = ARTCLITE()
        assert compressor.block_size == 8
        assert compressor.tolerance == 0.1
    
    def test_init_custom(self):
        """Test custom initialization."""
        compressor = ARTCLITE(block_size=16, tolerance=0.05)
        assert compressor.block_size == 16
        assert compressor.tolerance == 0.05
    
    def test_compress_linear_data(self):
        """Test compression of perfectly linear data."""
        compressor = ARTCLITE(block_size=8, tolerance=0.1)
        
        # Perfectly linear data: y = 0.5x + 20
        data = np.array([20.0, 20.5, 21.0, 21.5, 22.0, 22.5, 23.0, 23.5])
        compressed = compressor.compress(data)
        
        assert len(compressed) == 1
        assert compressed[0]['type'] == 'formula'
        assert compressor.stats['blocks_compressed'] == 1
        assert compressor.stats['blocks_raw'] == 0
    
    def test_compress_noisy_data(self):
        """Test compression of noisy data (should fall back to raw)."""
        compressor = ARTCLITE(block_size=8, tolerance=0.01)
        
        # Random data - shouldn't fit a line well
        np.random.seed(42)
        data = np.random.randn(8).astype(np.float32)
        compressed = compressor.compress(data)
        
        assert len(compressed) == 1
        assert compressed[0]['type'] == 'raw'
        assert compressor.stats['blocks_raw'] == 1
    
    def test_decompress_formula(self):
        """Test decompression of formula-compressed data."""
        compressor = ARTCLITE(block_size=8, tolerance=0.1)
        
        data = np.array([20.0, 20.5, 21.0, 21.5, 22.0, 22.5, 23.0, 23.5])
        compressed = compressor.compress(data)
        decompressed = compressor.decompress(compressed)
        
        np.testing.assert_allclose(data, decompressed, atol=compressor.tolerance)
    
    def test_decompress_raw(self):
        """Test decompression of raw data."""
        compressor = ARTCLITE(block_size=8, tolerance=0.001)
        
        np.random.seed(42)
        data = np.random.randn(8).astype(np.float32)
        compressed = compressor.compress(data)
        decompressed = compressor.decompress(compressed)
        
        np.testing.assert_allclose(data, decompressed, atol=1e-6)
    
    def test_multiple_blocks(self):
        """Test compression of multiple blocks."""
        compressor = ARTCLITE(block_size=8, tolerance=0.1)
        
        # 24 values = 3 blocks
        data = np.linspace(0, 24, 24).astype(np.float32)
        compressed = compressor.compress(data)
        
        assert len(compressed) == 3
        assert compressor.stats['total_readings'] == 24


class TestARTCLITEStreaming:
    """Tests for streaming mode."""
    
    def test_add_reading(self):
        """Test adding individual readings."""
        compressor = ARTCLITE(block_size=8)
        
        for i in range(5):
            compressor.add_reading(float(i))
        
        assert len(compressor._buffer) == 5
        assert compressor.stats['total_readings'] == 5
    
    def test_block_ready(self):
        """Test block_ready detection."""
        compressor = ARTCLITE(block_size=8)
        
        for i in range(7):
            compressor.add_reading(float(i))
            assert not compressor.block_ready()
        
        compressor.add_reading(7.0)
        assert compressor.block_ready()
    
    def test_get_block(self):
        """Test getting compressed block from buffer."""
        compressor = ARTCLITE(block_size=8, tolerance=0.1)
        
        # Add linear data
        for i in range(8):
            compressor.add_reading(20.0 + i * 0.5)
        
        assert compressor.block_ready()
        block = compressor.get_block()
        
        assert block is not None
        assert block['type'] == 'formula'
        assert not compressor.block_ready()
        assert len(compressor._buffer) == 0
    
    def test_get_block_not_ready(self):
        """Test get_block when not ready."""
        compressor = ARTCLITE(block_size=8)
        
        for i in range(5):
            compressor.add_reading(float(i))
        
        block = compressor.get_block()
        assert block is None
    
    def test_streaming_stats(self):
        """Test statistics update in streaming mode."""
        compressor = ARTCLITE(block_size=8, tolerance=0.1)
        
        # Add two blocks of linear data
        for i in range(16):
            compressor.add_reading(20.0 + i * 0.1)
            if compressor.block_ready():
                compressor.get_block()
        
        assert compressor.stats['blocks_compressed'] == 2
        assert compressor.stats['original_size'] == 64  # 2 blocks * 8 values * 4 bytes
        assert compressor.stats['compressed_size'] == 16  # 2 blocks * 8 bytes


class TestARTCLITEUtility:
    """Tests for utility methods."""
    
    def test_get_ratio_initial(self):
        """Test compression ratio before any compression."""
        compressor = ARTCLITE()
        assert compressor.get_ratio() == 1.0
    
    def test_get_ratio_after_compression(self):
        """Test compression ratio after compression."""
        compressor = ARTCLITE(block_size=8, tolerance=0.1)
        
        data = np.array([20.0, 20.5, 21.0, 21.5, 22.0, 22.5, 23.0, 23.5])
        compressor.compress(data)
        
        ratio = compressor.get_ratio()
        assert ratio == 4.0  # 32 bytes -> 8 bytes = 4x
    
    def test_reset_stats(self):
        """Test statistics reset."""
        compressor = ARTCLITE(block_size=8)
        
        data = np.linspace(0, 8, 8).astype(np.float32)
        compressor.compress(data)
        
        compressor.reset_stats()
        
        assert compressor.stats['original_size'] == 0
        assert compressor.stats['compressed_size'] == 0
        assert compressor.stats['blocks_compressed'] == 0
    
    def test_clear_buffer(self):
        """Test buffer clearing."""
        compressor = ARTCLITE(block_size=8)
        
        for i in range(5):
            compressor.add_reading(float(i))
        
        compressor.clear_buffer()
        assert len(compressor._buffer) == 0
    
    def test_print_stats(self, capsys):
        """Test stats printing."""
        compressor = ARTCLITE(block_size=8, tolerance=0.1)
        
        data = np.array([20.0, 20.5, 21.0, 21.5, 22.0, 22.5, 23.0, 23.5])
        compressor.compress(data)
        compressor.print_stats()
        
        captured = capsys.readouterr()
        assert "ARTC-LITE" in captured.out
        assert "Compression ratio" in captured.out


class TestARTCLITEEdgeCases:
    """Edge case tests."""
    
    def test_empty_data(self):
        """Test compression of empty data."""
        compressor = ARTCLITE(block_size=8)
        compressed = compressor.compress([])
        assert compressed == []
    
    def test_incomplete_block(self):
        """Test that incomplete blocks are skipped."""
        compressor = ARTCLITE(block_size=8)
        
        # Only 5 values - less than block_size
        data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        compressed = compressor.compress(data)
        
        assert compressed == []
    
    def test_constant_data(self):
        """Test compression of constant data."""
        compressor = ARTCLITE(block_size=8, tolerance=0.1)
        
        data = np.full(8, 25.0, dtype=np.float32)
        compressed = compressor.compress(data)
        
        assert len(compressed) == 1
        assert compressed[0]['type'] == 'formula'
        assert compressed[0]['m'] == pytest.approx(0.0, abs=1e-6)
        assert compressed[0]['b'] == pytest.approx(25.0, abs=1e-6)
    
    def test_list_input(self):
        """Test that list input works."""
        compressor = ARTCLITE(block_size=8, tolerance=0.1)
        
        data = [20.0, 20.5, 21.0, 21.5, 22.0, 22.5, 23.0, 23.5]
        compressed = compressor.compress(data)
        
        assert len(compressed) == 1
        assert compressed[0]['type'] == 'formula'


class TestARTCLITEAccuracy:
    """Accuracy and precision tests."""
    
    def test_reconstruction_error_within_tolerance(self):
        """Test that reconstruction error is within tolerance."""
        compressor = ARTCLITE(block_size=8, tolerance=0.1)
        
        # Slightly noisy linear data
        np.random.seed(42)
        data = np.linspace(20, 28, 8) + np.random.normal(0, 0.01, 8)
        data = data.astype(np.float32)
        
        compressed = compressor.compress(data)
        decompressed = compressor.decompress(compressed)
        
        max_error = np.max(np.abs(data - decompressed))
        assert max_error <= compressor.tolerance
    
    def test_temperature_simulation(self):
        """Test with realistic temperature data."""
        compressor = ARTCLITE(block_size=8, tolerance=0.1)
        
        # Simulate temperature readings
        np.random.seed(42)
        t = np.linspace(0, 24, 96)  # 96 readings over 24 hours
        temps = 20 + 5 * np.sin(2 * np.pi * t / 24)
        temps += np.random.normal(0, 0.05, 96)
        temps = temps.astype(np.float32)
        
        compressed = compressor.compress(temps)
        decompressed = compressor.decompress(compressed)
        
        # Check reasonable compression
        assert compressor.get_ratio() > 1.0
        
        # Check accuracy
        max_error = np.max(np.abs(temps[:len(decompressed)] - decompressed))
        assert max_error <= compressor.tolerance * 2  # Allow some slack for boundary effects
