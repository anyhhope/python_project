import cv2
from multiprocessing import Process, Event
from .schema import MessageConsume

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

        # state_message: MessageState = {"id": data_object.id, "state": StateEnum.STARTUP_PROCESS.value}
        # await produce(state_message) 
        
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