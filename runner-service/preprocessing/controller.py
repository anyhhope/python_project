from .schema import MessageConsume
from producer import AIOProducer
from config import cfg
import cv2
from types import SimpleNamespace


def get_query_producer() -> AIOProducer:
    return AIOProducer(cfg, produce_topic=cfg.query_topic)

async def process(message_consumed: MessageConsume):
    print(f"Message {message_consumed} consumed")
    data_object: MessageConsume = SimpleNamespace(**message_consumed)

    cap = cv2.VideoCapture(data_object.rtsp_src)
    if not cap.isOpened():
        print("Error: Could not open RTSP stream.")
        exit()
    while True:
        ret, frame = cap.read()
        if not ret:
            print('Error: No frame received from stream.')
            break

        cv2.imshow("RTSP Stream", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

    return 