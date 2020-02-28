import face_recognition
import base64
import cv2
import json
import time
from cache import redis_instance


def stream_faces(ws):
    detection_method = 'hog'
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS, 20)

    cap.set(3, 320)
    cap.set(4, 240)

    while True:
        _, img = cap.read()

        if int(redis_instance.get('flag')) == 0:
            continue

        boxes = face_recognition.face_locations(
            img,
            model=detection_method
        )

        if len(boxes):
            for (x, w, h, y) in boxes:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = img[x:x+w, y:h]
                encoded_img = cv2.imencode('.jpg', img)[1]
                encoded_img = base64.b64encode(encoded_img).decode()

            data = {
                "origin": "na porta do laboratório",
                "image": encoded_img
            }

            if int(redis_instance.get('flag')) == 1:
                redis_instance.set('flag', 1)
                ws.send(json.dumps(data))

        cv2.imshow('image', img)
        k = cv2.waitKey(100) & 0xff

        if k == 27:
            break

        time.sleep(0.5)

    cap.release()
    cv2.destroyAllWindows()
