import cv2
from multiprocessing import Process, Event
from .schema import MessageConsume, MessageState, StateEnum
from producer import AIOProducer
from config import cfg


class CustomProcess(Process):

    def __init__(self, msg : MessageConsume):
        Process.__init__(self)
        self.event = Event()
        self.msg = msg
 
    def run(self):
        cap = cv2.VideoCapture(self.msg.rtsp_src)
        if not cap.isOpened():
            print("Error: Could not open RTSP stream.")
            return

        # producer: AIOProducer = get_state_producer()
        # state_message: MessageState = {"id": self.msg.id, "state": StateEnum.RUNNER_PROCESS.value}
        # await produce(producer, state_message) 
        # producer.stop()
        
        window_name = f"RTSP Stream {self.msg.id}"  
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

        while True:
            ret, frame = cap.read()
            if not ret:
                print('Error: No frame received from stream.')
                break

            cv2.imshow(window_name, frame)

            if self.event.is_set():
                break

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
        cap.release()
        cv2.destroyWindow(window_name)

#  process.event.set() - to stop loop -> stop process