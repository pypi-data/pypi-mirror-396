"""
ARTC-LITE Example:  Temperature Sensor
Simulates 24 hours of temperature readings from an IoT sensor
"""

from artc import ARTCLITE
import numpy as np


def main():
    print("=" * 60)
    print("ARTC-LITE:  Temperature Sensor Example")
    print("=" * 60)
    
    # Simulate 24 hours of temperature data (100 readings)
    print("\n📡 Simulating temperature sensor...")
    np.random.seed(42)
    t = np.linspace(0, 24, 100)
    
    # Daily temperature cycle + small noise (realistic sensor)
    temperature = 20 + 5 * np.sin(2 * np.pi * t / 24)
    temperature += np.random.normal(0, 0.05, 100)
    
    print(f"   Collected {len(temperature)} readings over 24 hours")
    print(f"   Temperature range: {temperature.min():.1f}°C to {temperature.max():.1f}°C")
    print(f"   First 5 readings: {temperature[:5]}")
    
    # Compress with ARTC-LITE
    print("\n🗜️  Compressing with ARTC-LITE...")
    compressor = ARTCLITE(block_size=8, tolerance=0.1)
    compressed = compressor.compress(temperature)
    
    # Show results
    print("\n📊 Results:")
    compressor.print_stats()
    
    # Decompress
    print("\n🔄 Decompressing...")
    decompressed = compressor.decompress(compressed)
    
    # Verify accuracy
    max_error = np.max(np.abs(temperature[:len(decompressed)] - decompressed))
    print(f"   Max reconstruction error: {max_error:.4f}°C")
    
    if max_error <= compressor.tolerance:
        print("\n✅ SUCCESS! Data compressed and reconstructed accurately")
        print(f"   Original:   {compressor.stats['original_size']} bytes")
        print(f"   Compressed: {compressor.stats['compressed_size']} bytes")
        print(f"   Saved: {compressor.stats['original_size'] - compressor.stats['compressed_size']} bytes")
        print(f"   That's {compressor.get_ratio():.1f}x smaller!  🎉")
    else:
        print(f"\n⚠️  Error {max_error:.4f}°C exceeds tolerance {compressor.tolerance}°C")
    
    # Show what compressed data looks like
    print("\n📦 Sample compressed blocks:")
    for i, block in enumerate(compressed[:3]):
        if block['type'] == 'formula':
            print(f"   Block {i}:  FORMULA (m={block['m']:.4f}, b={block['b']:.4f}) - 8 bytes")
        else:
            print(f"   Block {i}: RAW ({len(block['data'])} values) - {len(block['data'])*4} bytes")
    
    if len(compressed) > 3:
        print(f"   ...  and {len(compressed)-3} more blocks")


if __name__ == "__main__":
    main()
