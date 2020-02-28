import face_recognition
import base64
import cv2
import json
import time
from cache import redis_instance


def stream_faces(ws):
    detection_method = 'hog'
    cap = cv2.VideoCapture(0)

    cap.set(3, 640)
    cap.set(4, 480)

    while True:
        _, img = cap.read()

        if int(redis_instance.get('flag')) == 0:
            time.sleep(2)
            continue

        boxes = face_recognition.face_locations(
            img,
            model=detection_method
        )

        if len(boxes):
            for (x, w, h, y) in boxes:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = img[y:y+h, x:x+w]
                encoded_img = cv2.imencode('.jpg', img)[1]
                encoded_img = base64.b64encode(encoded_img).decode()

            data = {
                "origin": "na porta do laboratório",
                "image": encoded_img
            }
            ws.send(json.dumps(data))

        cv2.imshow('image', img)
        k = cv2.waitKey(10) & 0xff

        time.sleep(1)

        if k == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
