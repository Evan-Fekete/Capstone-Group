from ultralytics import YOLO
import cv2
import math
import time
import json


def look_around(find_object):
    class_names = ["apple", "medicine", "mug", "remote", "shoe", "user"]

    if find_object in class_names:
        # start webcam

        # Uncomment for Linux
        cap = cv2.VideoCapture(0)

        # # Uncomment for Windows
        # cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        cap.set(3, 640)
        cap.set(4, 480)
        # model
        model = YOLO("yolo-Weights/NK01_model_v1.pt")

        current = time.time()
        runtime = 0.5
        found_result = [False, 0, 0]  # default if nothing detected

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
                    # bounding box
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(
                        x2), int(y2)  # convert to int values
                    cls = int(box.cls[0])

                    # put box in cam
                    cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

                    # confidence
                    confidence = math.ceil((box.conf[0]*100))/100
                    print("Confidence --->", confidence)

                    # class name
                    print("Class name -->", class_names[cls])

                    # Dimensions
                    found_result = dimenisons(
                        find_object, class_names[cls], x1, y1, x2, y2)

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
        print("From appp.py to dimenisons")
        # print(find_object)
        # print(found_result[0])
        # print(found_result[1])
        # print(found_result[2])
        # print(found_result[3])
        # print(found_result[4])
        return [found_result[0], found_result[1], found_result[2],found_result[3],found_result[4]]
    else:
        print("Object does not exist in this environment")
        return None

def dimenisons(find_object, class_names, x1, y1, x2, y2):
    bounding_x = int(x2) - int(x1)
    bounding_y = int(y2) - int(y1)
    offset_x = (int(x2) + int(x1))/2
    print("Dimenison X of Bounding Box -->", bounding_x)
    print("Dimenison Y of Bounding Box -->", bounding_y)
    print("Offset -->", offset_x)
    if (find_object == class_names and 355 < bounding_x and 306 < bounding_y):
        print("You are in front of mug")
        return [find_object,True, bounding_x, bounding_y,offset_x ]
    elif (find_object == class_names):
        print("You are in front of apple")
        return [find_object,True, bounding_x, bounding_y,offset_x ]
    elif (find_object == class_names and 217 < bounding_x and 365 < bounding_y):
        print("You are in front of medicine")
        return [find_object,True, bounding_x, bounding_y,offset_x ]
    elif (find_object == class_names and 265 < bounding_x and 455 < bounding_y):
        print("You are in front of user")
        return [find_object,True, bounding_x, bounding_y,offset_x ]
    else:
        print("No object found")
        return [find_object,False, bounding_x, bounding_y,offset_x ]


if __name__ == "__main__":
    with open('object.JSON', 'r') as input:
        query = json.load(input)
    look_around(query.get("object"))
