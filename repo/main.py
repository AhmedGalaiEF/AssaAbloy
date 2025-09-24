import spidev
import time


import sys, os
sys.path.append(r"C:\Users\Ahmed Galai\Desktop\dev\dev")
import api_util as sdk

# Predefined evacuate function
def evacuate():
    print("FIRE ALARM TRIGGERED! Evacuate now!")
    # Add actual evacuation code here (sirens, notifications, etc.)
    x_token = sdk.get_token()
    task_id = ''
    r = sdk.execute_task(x_token, task_id)

# # SPI setup for MCP3008 ADC
# spi = spidev.SpiDev()
# spi.open(0, 0)  # Bus 0, Device (CS) 0
# spi.max_speed_hz = 1350000

# # Read MCP3008 channel function
# def read_adc(channel):
#     if channel < 0 or channel > 7:
#         raise ValueError("ADC channel must be 0-7")
#     adc = spi.xfer2([1, (8 + channel) << 4, 0])
#     data = ((adc[1] & 3) << 8) + adc[2]
#     return data  # 0-1023 range (10-bit ADC)

# # Configurable thresholds
# ACTIVE_THRESHOLD = 700   # e.g., >700 means alarm (active high)
# PASSIVE_THRESHOLD = 300  # e.g., <300 means alarm (active low)

# # Mode: "active" or "passive"
# MODE = "active"  # Change to "passive" for active-low circuits

# try:
#     while True:
#         value = read_adc(0)  # Read from channel 0
#         print(f"Analog value: {value}")

#         if MODE == "active" and value > ACTIVE_THRESHOLD:
#             evacuate()
#         elif MODE == "passive" and value < PASSIVE_THRESHOLD:
#             evacuate()

#         time.sleep(0.5)

# except KeyboardInterrupt:
#     spi.close()
#     print("Stopped monitoring.")

import RPi.GPIO as GPIO
import time

# Use BCM pin numbering
GPIO.setmode(GPIO.BCM)

# List of input pins you want to check
input_pins = [17, 27, 22]  # Change these to your desired GPIO pins

# Set up pins as inputs with pull-down resistors
for pin in input_pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

print("Reading GPIO inputs (press Ctrl+C to exit)...")

try:
    while True:
        for pin in input_pins:
            state = GPIO.input(pin)
            print(f"GPIO {pin}: {'HIGH' if state else 'LOW'}")
        time.sleep(0.5)  # Delay between readings
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    GPIO.cleanup()
