"""
Tests for ARTC: Base Compression Algorithm
"""

import pytest
import numpy as np
from artc import ARTC


class TestARTCBasic:
    """Basic functionality tests."""
    
    def test_init_defaults(self):
        """Test default initialization."""
        compressor = ARTC()
        assert compressor.block_size == 16
        assert compressor.tolerance == 0.1
    
    def test_init_custom(self):
        """Test custom initialization."""
        compressor = ARTC(block_size=32, tolerance=0.05)
        assert compressor.block_size == 32
        assert compressor.tolerance == 0.05
    
    def test_compress_linear_data(self):
        """Test compression of perfectly linear data."""
        compressor = ARTC(block_size=16, tolerance=0.1)
        
        # Perfectly linear data
        data = np.linspace(0, 15, 16).astype(np.float32)
        compressed = compressor.compress(data)
        
        assert len(compressed) == 1
        assert compressed[0]['type'] == 'formula'
        assert compressor.stats['blocks_compressed'] == 1
        assert compressor.stats['blocks_raw'] == 0
    
    def test_compress_noisy_data(self):
        """Test compression of noisy data."""
        compressor = ARTC(block_size=16, tolerance=0.01)
        
        np.random.seed(42)
        data = np.random.randn(16).astype(np.float32)
        compressed = compressor.compress(data)
        
        assert len(compressed) == 1
        assert compressed[0]['type'] == 'raw'
    
    def test_decompress(self):
        """Test decompression."""
        compressor = ARTC(block_size=16, tolerance=0.1)
        
        data = np.linspace(0, 15, 16).astype(np.float32)
        compressed = compressor.compress(data)
        decompressed = compressor.decompress(compressed)
        
        np.testing.assert_allclose(data, decompressed, atol=compressor.tolerance)
    
    def test_multiple_blocks(self):
        """Test compression of multiple blocks."""
        compressor = ARTC(block_size=16, tolerance=0.1)
        
        data = np.linspace(0, 63, 64).astype(np.float32)
        compressed = compressor.compress(data)
        
        assert len(compressed) == 4
        assert compressor.stats['total_values'] == 64
    
    def test_get_ratio(self):
        """Test compression ratio calculation."""
        compressor = ARTC(block_size=16, tolerance=0.1)
        
        data = np.linspace(0, 15, 16).astype(np.float32)
        compressor.compress(data)
        
        ratio = compressor.get_ratio()
        assert ratio == 8.0  # 64 bytes -> 8 bytes
    
    def test_print_stats(self, capsys):
        """Test stats printing."""
        compressor = ARTC(block_size=16, tolerance=0.1)
        
        data = np.linspace(0, 15, 16).astype(np.float32)
        compressor.compress(data)
        compressor.print_stats()
        
        captured = capsys.readouterr()
        assert "ARTC Compression Stats" in captured.out


class TestARTCEdgeCases:
    """Edge case tests."""
    
    def test_empty_data(self):
        """Test compression of empty data."""
        compressor = ARTC(block_size=16)
        compressed = compressor.compress([])
        assert compressed == []
    
    def test_incomplete_block(self):
        """Test that incomplete blocks are skipped."""
        compressor = ARTC(block_size=16)
        
        data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        compressed = compressor.compress(data)
        
        assert compressed == []
    
    def test_constant_data(self):
        """Test compression of constant data."""
        compressor = ARTC(block_size=16, tolerance=0.1)
        
        data = np.full(16, 42.0, dtype=np.float32)
        compressed = compressor.compress(data)
        
        assert len(compressed) == 1
        assert compressed[0]['type'] == 'formula'
        assert compressed[0]['m'] == pytest.approx(0.0, abs=1e-6)
        assert compressed[0]['b'] == pytest.approx(42.0, abs=1e-6)
    
    def test_list_input(self):
        """Test that list input works."""
        compressor = ARTC(block_size=16, tolerance=0.1)
        
        data = list(range(16))
        compressed = compressor.compress(data)
        
        assert len(compressed) == 1
