from ultralytics import YOLO
import cv2
import math
import time
import json


def look_around(find_object):
    class_names = ["apple", "medicine", "mug", "remote", "shoe", "user"]
    # class_names = ["user"]

    if find_object in class_names:
        # start webcam
        cap = cv2.VideoCapture(0)
        cap.set(3, 640)
        cap.set(4, 480)

        # model
        model = YOLO("yolo-Weights/NK01_model_v1.pt")

        # object classes
        target = class_names.index(find_object)

        current = time.time()
        runtime = 10
        print("TARGET:", find_object, "ID:", target)
        while True:

            if time.time()-current > runtime:
                print("Detection complete")
                break

            success, img = cap.read()
            results = model(img, stream=True)

            # coordinates
            for r in results:
                boxes = r.boxes

                for box in boxes:
                    cls = int(box.cls[0])
                    if cls != target:
                        continue
                    # bounding box
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(
                        x2), int(y2)  # convert to int values

                    # put box in cam
                    cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

                    # confidence
                    confidence = math.ceil((box.conf[0]*100))/100
                    print("Confidence --->", confidence)

                    # class name
                    cls = int(box.cls[0])
                    print("Class name -->", class_names[cls])

                    # object details
                    org = [x1, y1]
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    fontScale = 1
                    color = (96, 86, 20)
                    thickness = 2

                    label = f"class: {class_names[cls]} conf:{confidence}"
                    cv2.putText(img, label, org, font,
                                fontScale, color, thickness)

            cv2.imshow('Webcam', img)
            if cv2.waitKey(1) == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
    else:
        print("Object does not exist in this environment")


with open('object.JSON', 'r') as input:
    query = json.load(input)

look_around(query.get("object"))
