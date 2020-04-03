import base64
import cv2
import json


def stream_faces(ws):
    cascadePath = "cascades/haarcascade_frontalface_alt.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath)

    cap = cv2.VideoCapture(1)

    cap.set(3, 320)
    cap.set(4, 240)

    while True:
        _, img = cap.read()

        if not ws.producer.acquire(blocking=False):
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
                "origin": "127.0.0.1",
                "image": encoded_img
            }

            ws.send(json.dumps(data))
            ws.consumer.release()
        else:
            ws.producer.release()

        cv2.imshow('image', img)
        k = cv2.waitKey(30) & 0xff

        if k == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
