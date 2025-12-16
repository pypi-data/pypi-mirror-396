"""
ARTC-LITE IoT Demo:  Streaming Mode
Shows how to use ARTC-LITE with real-time sensor data
"""

from artc import ARTCLITE
import numpy as np
import time


def simulate_sensor_reading():
    """Simulate reading from a temperature sensor."""
    # In real code, this would be:   sensor.read_temperature()
    base_temp = 22.0
    variation = np.random.normal(0, 0.1)
    return base_temp + variation


def send_over_network(compressed_block):
    """
    Simulate sending compressed data over LoRa/WiFi/Bluetooth. 
    
    In real code, this would be: 
    - LoRa:  lora.send(compressed_block)
    - WiFi: requests.post(url, json=compressed_block)
    - Bluetooth: ble.write(compressed_block)
    """
    print(f"   📤 Sending:  {compressed_block}")


def main():
    print("=" * 60)
    print("ARTC-LITE:  IoT Streaming Demo")
    print("=" * 60)
    print("\nSimulating real-time sensor with periodic transmission...\n")
    
    # Initialize compressor
    compressor = ARTCLITE(block_size=8, tolerance=0.1)
    
    # Simulate 50 sensor readings
    for i in range(50):
        # Read from sensor
        reading = simulate_sensor_reading()
        print(f"Reading {i+1}: {reading:.2f}°C", end="")
        
        # Add to compressor
        compressor.add_reading(reading)
        
        # Check if block is ready
        if compressor.block_ready():
            compressed_block = compressor.get_block()
            
            if compressed_block['type'] == 'formula':
                print(f" → ✅ COMPRESSED (formula) - 8 bytes")
            else:
                print(f" → ⚠️  RAW - {len(compressed_block['data'])*4} bytes")
            
            send_over_network(compressed_block)
        else:
            print(" → 📦 Buffering...")
        
        # Simulate time between readings
        time.sleep(0.1)
    
    print("\n" + "=" * 60)
    print("Final Statistics:")
    print("=" * 60)
    compressor.print_stats()
    
    # Calculate savings
    if compressor.stats['original_size'] > 0:
        bytes_saved = compressor.stats['original_size'] - compressor.stats['compressed_size']
        print(f"\n💾 Bytes saved: {bytes_saved} bytes")
        print(f"📡 Network bandwidth reduced by {(1 - 1/compressor.get_ratio())*100:.0f}%")
        print(f"🔋 Battery life extended by ~{compressor.get_ratio():.1f}x (less transmission)")


if __name__ == "__main__":
    main()
