import cv2
from multiprocessing import Process, Event
from .schema import MessageConsume, MessageState, StateEnum, ServiceSenderEnum
from producer import AIOProducer
from config import cfg
from producer import get_frame_producer, produce
import asyncio
import base64


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
        try:
            cap = cv2.VideoCapture(self.msg.rtsp_src)
            if not cap.isOpened():
                print("Error: Could not open RTSP stream.")
                return

            fps = int(cap.get(cv2.CAP_PROP_FPS))
            cnt = 0

            producerFrame: AIOProducer = get_frame_producer()

            while True:
                ret, frame = cap.read()
                if not ret:
                    print('Error: No frame received from stream.')
                    raise Exception

                if self.event.is_set():
                    break
                
                cnt += 1
                if ret and cnt % (fps * 4) == 0:
                    cnt += 1
                    img_bytes = cv2.imencode(".jpg", frame)[1].tobytes()
                    img_base64 = base64.b64encode(img_bytes).decode('utf-8') 
                    frame_message = {"id": self.id, "frame_id": str(cnt), "frame": img_base64}
                    await produce(producerFrame, frame_message)
                    print(f"Frame msg produced")

                if ret and cnt == 1:
                    state_message: MessageState = {"id": self.msg.id, "state": StateEnum.RUNNER_PROCESS.value, "error": False, "sender": ServiceSenderEnum.RUNNER.value}
                    await produce(producerFrame, state_message, topic=cfg.state_topic)
                    
            await producerFrame.stop()
            cap.release()
        
        except Exception as e:
            producerFrame: AIOProducer = get_frame_producer()
            state_message: MessageState = {"id": self.msg.id, "state": StateEnum.SHUTDOWN.value, "error": True, "sender": ServiceSenderEnum.RUNNER.value}
            await produce(producerFrame, state_message, topic=cfg.state_topic)
            await producerFrame.stop()
            print(f"Process {self.id} ERROR: {e}")
            self.kill()


#  process.event.set() - to stop loop -> stop process