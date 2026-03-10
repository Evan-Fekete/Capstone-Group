import serial
import time
import json
from app import look_around
from app import dimenisons

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

    send_command("SERVO PAN 45")
    time.sleep(3)
    send_command("SERVO TILT 110")
    time.sleep(3)
    # send_command("SWIVEL_L")
    # time.sleep(1)
    # send_command("SWIVEL_R")
    # time.sleep(1)


    # Step 1: Search - move slowly while looking
    print("--- PHASE 1: SEARCHING ---")
    send_command("SEARCH")
    time.sleep(1)

    result = look_around(target)

    if result is None:
        print("Invalid object")
        send_command("STOP")
        return

    obj, found, bx, by, offset_x= result

    # print(f"before bounding box x: {bx}")
    # print(f"before bounding box y: {by}")

    if found:
        # Step 2: Move toward object
        print(f"--- PHASE 2: FOUND {obj}! APPROACHING ---")
        result = look_around(target)
        obj, found, bx, by , offset_x= result
        print(f"before while bounding box x: {bx}")
        print(f"before while bounding box y: {by}")
        print(f"before while bounding box y: {offset_x}")
        while (bx < 103 and by < 103):
            r = look_around(target)
            obj, found, bx, by , offset_x = r
            print(f"bounding box x: {bx}")
            print(f"bounding box y: {by}")
            print(f"offset: {offset_x}")
            if (100 < offset_x < 330):
                send_command("S_LEFT")
                print("Moving left")

            elif (345 < offset_x < 600):
                send_command("S_RIGHT")
                print("Moving Right")

            else:
                send_command("FORWARD")
                print("Moving forward")
        send_command("STOP")
        send_command("SERVO TILT 110")
        print("Tilting camera")

        time.sleep(3)

        # Step 3: Stop and pickup
        print("--- PHASE 3: PICKUP ---")
        send_command("STOP")
        time.sleep(1)
        # send_command("PICKUP")
        # time.sleep(3)

        # Step 4: Return
        # print("--- PHASE 4: RETURNING ---")
        # send_command("BACKWARD")
        time.sleep(3)
        send_command("STOP")
        print("--- COMPLETE ---")
    else:
        print("Object not found.")
        send_command("STOP")

    ser.close()


if __name__ == "__main__":
    main()
