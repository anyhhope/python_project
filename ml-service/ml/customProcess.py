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
from data import get_connection, PoolConnectionProxy, Database
from . import controller


class CustomProcess(Process):

    def __init__(self, id: str):
        Process.__init__(self)
        self.event = Event()
        self.id = id
        self.msg_queue = Queue()
        self.db_instance = Database(cfg)

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.async_run())
 
    async def async_run(self):
        try:
            model = YOLO(cfg.ml_model_path)
            print(cfg.ml_model_path)

            producerState: AIOProducer = get_state_producer()
            state_message: MessageState = {"id": self.id, "state": StateEnum.ML_PROCESS.value, "error": False, "sender": ServiceSenderEnum.ML.value}
            await produce(producerState, state_message)
            await producerState.stop()

            await self.db_instance.connect()
            db_conn: PoolConnectionProxy = await get_connection(self.db_instance)

            while not self.event.is_set(): 
                if self.event.is_set():
                    break

                msg: MessageConsume = self.msg_queue.get()
                img_bytes = base64.b64decode(msg.frame)
                img = Image.open(BytesIO(img_bytes))

                results = model([img]) 

                for result in results:  
                    img = result.plot()

                    try:
                        async with db_conn.transaction():
                            filename = f"frame_{msg.id}_{msg.frame_id}.jpg"
                            s3_url = await controller.upload_img_to_s3(img, filename)
                            await controller.save_detection_to_db(db_conn, s3_url, msg, result)
                    except Exception as e:
                        print(f"Error s3 and pg transaction: {e}")
                        raise e
                    
            print("HERE")
            await self.db_instance.disconnect()

        except Exception as e:
            producerState: AIOProducer = get_state_producer()
            state_message: MessageState = {"id": self.id, "state": StateEnum.SHUTDOWN.value, "error": True, "sender": ServiceSenderEnum.ML.value}
            await produce(producerState, state_message)
            await producerState.stop()
            await self.db_instance.disconnect()
            print(f"ML process {self.id} error : {e}")
            self.kill()
               

    def send_message(self, msg: MessageConsume):
        # Помещение сообщения в очередь
        self.msg_queue.put(msg)

    def stop(self):
        # Установка флага остановки
        self.event.set()
   

#  process.event.set() - to stop loop -> stop process