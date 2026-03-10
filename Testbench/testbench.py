import serial
import time
import json
from app import look_around

# UART setup
ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)
time.sleep(2)  # wait for ESP32 to boot


def send_command(cmd):
    ser.write(f'{cmd}\n'.encode())
    time.sleep(0.1)
    if ser.in_waiting:
        return ser.readline().decode().strip()
    return None


def main():
    # load target object
    with open('object.JSON', 'r') as f:
        query = json.load(f)

    target = query.get("object")
    print(f"Looking for: {target}")

    # Step 1: Search - move slowly while looking
    print("--- PHASE 1: SEARCHING ---")
    send_command("SEARCH")
    time.sleep(1)

    result = look_around(target)

    if result is None:
        print("Invalid object")
        send_command("STOP")
        return

    obj, found, bx, by, offset_x = result

    print(f"before bounding box x: {bx}")
    print(f"before bounding box y: {by}")

    if found:
        # Step 2: Move toward object
        print(f"--- PHASE 2: FOUND {obj} (box: {bx}x{by})! APPROACHING ---")
        while (bx < 70 and by < 70):
            result = look_around(target)
            obj, found, bx, by = result
            print(f"bounding box x: {bx}")
            print(f"bounding box y: {by}")
            if (offset_x > 0):
                send_command("LEFT")
                print("Moving left")

            elif (offset_x < 0):
                send_command("RIGHT")
                print("Moving Right")

            else:
                send_command("FORWARD")
                print("Moving forward")
        send_command("SERVO TILT 90")
        print("Tilting camera")

        time.sleep(3)

        # Step 3: Stop and pickup
        print("--- PHASE 3: PICKUP ---")
        send_command("STOP")
        time.sleep(1)
        send_command("PICKUP")
        time.sleep(3)

        # Step 4: Return
        print("--- PHASE 4: RETURNING ---")
        send_command("BACKWARD")
        time.sleep(3)
        send_command("STOP")
        print("--- COMPLETE ---")
    else:
        print("Object not found.")
        send_command("STOP")

    ser.close()


if __name__ == "__main__":
    main()
