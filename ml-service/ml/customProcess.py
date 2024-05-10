import cv2
from multiprocessing import Process, Event
from .schema import MessageConsume
from producer import AIOProducer
from config import cfg
from producer import get_frame_producer, produce
import asyncio
import base64
from ultralytics import YOLO
from PIL import Image
from io import BytesIO


class CustomProcess(Process):

    def __init__(self, msg : MessageConsume, id: str):
        Process.__init__(self)
        self.event = Event()
        self.msg = msg
        self.id = id

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.async_run())
 
    async def async_run(self):
        model = YOLO('./yolo_model/yolov9c.pt')
        img_bytes = base64.b64decode(self.msg.frame)
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
            result.save(filename='result.jpg')  # save to disk

#  process.event.set() - to stop loop -> stop process