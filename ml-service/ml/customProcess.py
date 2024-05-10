import cv2
from multiprocessing import Process, Event, Queue
from .schema import MessageConsume, StateEnum, ServiceSenderEnum, MessageState
from producer import AIOProducer
from config import cfg
from producer import get_state_producer, produce
import asyncio
import base64
from ultralytics import YOLO
from PIL import Image
from io import BytesIO


class CustomProcess(Process):

    def __init__(self, id: str):
        Process.__init__(self)
        self.event = Event()
        self.id = id
        self.msg_queue = Queue()

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.async_run())
 
    async def async_run(self):
        model = YOLO(cfg.ml_model_path)
        producerState: AIOProducer = get_state_producer()
        state_message: MessageState = {"id": self.msg.id, "state": StateEnum.RUNNER_PROCESS.value, "error": False, "sender": ServiceSenderEnum.ML.value}
        await produce(producerState, state_message)

        while not self.event.is_set(): 

            msg: MessageConsume = self.msg_queue.get()
            img_bytes = base64.b64decode(msg.frame)
            img = Image.open(BytesIO(img_bytes))


            results = model([img]) 

            # Process results list
            for result in results:
                boxes = result.boxes  # Boxes object for bounding box outputs
                masks = result.masks  # Masks object for segmentation masks outputs
                keypoints = result.keypoints  # Keypoints object for pose outputs
                probs = result.probs  # Probs object for classification outputs
                obb = result.obb  # Oriented boxes object for OBB outputs
                result.show()  # display to screen
                result.save(filename=f'tmp/result{msg.id}_{msg.frame_id}.jpg')  # save to disk

    def send_message(self, msg: MessageConsume):
        # Помещение сообщения в очередь
        self.msg_queue.put(msg)

    def stop(self):
        # Установка флага остановки
        self.event.set()

    

#  process.event.set() - to stop loop -> stop process