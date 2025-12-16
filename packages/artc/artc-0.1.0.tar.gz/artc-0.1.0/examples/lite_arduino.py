"""
ARTC-LITE:  Arduino/C Implementation Guide

This shows the Python version alongside pseudocode for Arduino/C. 
The algorithm is simple enough to port to microcontrollers! 
"""

def arduino_pseudocode():
    """
    Shows how ARTC-LITE would look in Arduino C code.
    """
    
    code = """
// ====================================================================
// ARTC-LITE for Arduino
// Lightweight compression for sensor data
// ====================================================================

#define BLOCK_SIZE 8
#define TOLERANCE 0.1

float buffer[BLOCK_SIZE];
int buffer_count = 0;

// ====================================================================
// Add sensor reading to buffer
// ====================================================================
void artc_add_reading(float value) {
    buffer[buffer_count++] = value;
    
    if (buffer_count >= BLOCK_SIZE) {
        // Block ready - compress and send
        compress_and_send_block();
        buffer_count = 0;  // Reset
    }
}

// ====================================================================
// Compress one block
// ====================================================================
void compress_and_send_block() {
    // Calculate line fit:   y = mx + b
    float x_mean = 3.5;  // For block_size=8: (0+1+2+...+7)/8
    float y_mean = 0;
    
    for (int i = 0; i < BLOCK_SIZE; i++) {
        y_mean += buffer[i];
    }
    y_mean /= BLOCK_SIZE;
    
    // Calculate slope (m)
    float numerator = 0;
    float denominator = 0;
    
    for (int i = 0; i < BLOCK_SIZE; i++) {
        float x_diff = i - x_mean;
        float y_diff = buffer[i] - y_mean;
        numerator += x_diff * y_diff;
        denominator += x_diff * x_diff;
    }
    
    float m = numerator / denominator;
    float b = y_mean - m * x_mean;
    
    // Check error
    float max_error = 0;
    for (int i = 0; i < BLOCK_SIZE; i++) {
        float predicted = m * i + b;
        float error = abs(buffer[i] - predicted);
        if (error > max_error) max_error = error;
    }
    
    if (max_error <= TOLERANCE) {
        // Send compressed (just m and b)
        send_formula(m, b);
        Serial.println("Sent FORMULA (8 bytes)");
    } else {
        // Send raw
        send_raw(buffer, BLOCK_SIZE);
        Serial.println("Sent RAW (32 bytes)");
    }
}

// ====================================================================
// Send compressed formula over LoRa/WiFi
// ====================================================================
void send_formula(float m, float b) {
    // Example for LoRa
    LoRa.beginPacket();
    LoRa.write(0x01);  // Type: formula
    LoRa.write((byte*)&m, sizeof(float));
    LoRa.write((byte*)&b, sizeof(float));
    LoRa.endPacket();
}

// ====================================================================
// Arduino main loop
// ====================================================================
void loop() {
    // Read sensor
    float temp = readTemperature();
    
    // Add to ARTC-LITE
    artc_add_reading(temp);
    
    delay(1000);  // Read every second
}

// ====================================================================
// Memory usage: 
//   - Buffer: 8 floats × 4 bytes = 32 bytes
//   - Variables: ~20 bytes
//   - TOTAL: ~52 bytes of RAM
//
// Perfect for Arduino Uno (2KB RAM) or ESP32! 
// ====================================================================
    """
    
    print(code)


if __name__ == "__main__":
    print("=" * 60)
    print("ARTC-LITE: Arduino/C Implementation Guide")
    print("=" * 60)
    arduino_pseudocode()
