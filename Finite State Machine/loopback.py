import serial
# import serial.tools.list_ports
import time

# ports = serial.tools.list_ports.comports()
# for port in ports:
#     print(f"Device: {port.device}")
#     print(f"Description: {port.description}")
#     print(f"Hardware ID: {port.hwid}\n")

ser = serial.Serial('/dev/ttyAMA0', 9600)
time.sleep(1)

print(f"Connected to: {ser.name}")

test_string = b'Hello'

ser.write(test_string)
time.sleep(1)
received = ser.read(len(test_string))
print(received)

if received == test_string:
    print("Received:", received)
else:
    print("Nothing received - UART not working")

ser.close()