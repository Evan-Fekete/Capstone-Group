import serial
import time

ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)
time.sleep(1)

ser.write(b'Hello\n')
time.sleep(0.1)

if ser.in_waiting:
    print("Received:", ser.readline().decode().strip())
else:
    print("Nothing received - UART not working")

ser.close()