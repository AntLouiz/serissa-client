import base64
import cv2
import json
import time
from cache import redis_instance


def stream_faces(ws):
    cascadePath = "cascades/haarcascade_frontalface_alt.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath)

    cap = cv2.VideoCapture(0)

    cap.set(3, 320)
    cap.set(4, 240)

    while True:
        _, img = cap.read()

        if int(redis_instance.get('flag')) == 0:
            continue

        boxes = faceCascade.detectMultiScale(
            img,
            scaleFactor=1.2,
            minNeighbors=6
        )

        if len(boxes):
            for(x, y, w, h) in boxes:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = img[y:y+h, x:x+w]
                encoded_img = cv2.imencode('.jpg', img)[1]
                encoded_img = base64.b64encode(encoded_img).decode()

            data = {
                "origin": "na porta do laboratorio",
                "image": encoded_img
            }

            if int(redis_instance.get('flag')) == 1:
                redis_instance.set('flag', 1)
                ws.send(json.dumps(data))

        cv2.imshow('image', img)
        k = cv2.waitKey(30) & 0xff

        if k == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
