import cv2
from multiprocessing import Process, Event
from .schema import MessageConsume, MessageState, StateEnum, MessageFrame
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
        cap = cv2.VideoCapture(self.msg.rtsp_src)
        if not cap.isOpened():
            print("Error: Could not open RTSP stream.")
            return

        fps = int(cap.get(cv2.CAP_PROP_FPS))
        print(f"fps {fps}")
        cnt = 0

        producerFrame: AIOProducer = get_frame_producer()
        # producer: AIOProducer = get_state_producer()
        # state_message: MessageState = {"id": self.msg.id, "state": StateEnum.RUNNER_PROCESS.value}
        # await produce(producer, state_message) 
        # producer.stop()
        
        # window_name = f"RTSP Stream {self.msg.id}"  
        # cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

        while True:
            ret, frame = cap.read()
            if not ret:
                print('Error: No frame received from stream.')
                break

            # cv2.imshow(window_name, frame)

            if self.event.is_set():
                break
            
            cnt += 1
            if ret and cnt % (fps * 4) == 0:
                cnt += 1
                img_bytes = cv2.imencode(".jpg", frame)[1].tobytes()
                img_base64 = base64.b64encode(img_bytes).decode('utf-8') 
                frame_message = {"id": self.id, "frame_id": str(cnt), "frame": img_base64}
                # print(frame_message)
                await produce(producerFrame, frame_message)
                print(f"Frame msg produced")
                
        producerFrame.stop()
        cap.release()
        # cv2.destroyWindow(window_name)

#  process.event.set() - to stop loop -> stop process