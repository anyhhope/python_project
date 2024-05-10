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
from minio_connection import s3
import numpy as np
from data import get_connection, PoolConnectionProxy, Database
from . import db
from .models import DetectionDto


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
        print(cfg.ml_model_path)
        producerState: AIOProducer = get_state_producer()
        state_message: MessageState = {"id": self.id, "state": StateEnum.RUNNER_PROCESS.value, "error": False, "sender": ServiceSenderEnum.ML.value}
        await produce(producerState, state_message)
        await producerState.stop()

        while not self.event.is_set(): 

            msg: MessageConsume = self.msg_queue.get()
            img_bytes = base64.b64decode(msg.frame)
            img = Image.open(BytesIO(img_bytes))

            results = model([img]) 

            # Process results list
            for result in results:
                print("VERBOSE\n", result.verbose())
  
                img = result.plot()

                image = Image.fromarray(np.uint8(img))
                image_bytes = BytesIO()
                image.save(image_bytes, format='JPEG')
                image_bytes.seek(0)
                
                filename = f"frame_{msg.id}_{msg.frame_id}.jpg"
                s3.put_object(
                    cfg.minio_bucket,
                    filename,
                    image_bytes,
                    length=len(image_bytes.getvalue()),
                    content_type='image/jpeg'
                )

                s3_url = s3.presigned_get_object(bucket_name=cfg.minio_bucket, object_name=filename)
                print(s3_url)
                
                db_instance = Database(cfg)
                await db_instance.connect()
                new_row = DetectionDto(s3_url = s3_url, query_id = msg.id, 
                                        detection_result = result.verbose())
                db_conn: PoolConnectionProxy = await get_connection(db_instance)
                await db.insert_new_row(db_conn, new_row)

                result.save(filename=f'tmp/result{msg.id}_{msg.frame_id}.jpg')  
                

    def send_message(self, msg: MessageConsume):
        # Помещение сообщения в очередь
        self.msg_queue.put(msg)

    def stop(self):
        # Установка флага остановки
        self.event.set()

    

#  process.event.set() - to stop loop -> stop process