from .schema import MessageConsume, MessageState, StateEnum
from producer import AIOProducer
from config import cfg
import cv2
from types import SimpleNamespace
import asyncio


def get_state_producer() -> AIOProducer:
    return AIOProducer(cfg, produce_topic=cfg.state_topic)


async def produce(message_to_produce: MessageState):
    try:
        producer: AIOProducer = get_state_producer()
        await producer.send(value=message_to_produce)
        print(f"Message {message_to_produce} produced")
    except Exception as e:
        print(f"An error occurred: {e}")


async def process(message_consumed: MessageConsume):
    print(f"Message {message_consumed} consumed")
    data_object: MessageConsume = SimpleNamespace(**message_consumed)

    cap = cv2.VideoCapture(data_object.rtsp_src)
    if not cap.isOpened():
        print("Error: Could not open RTSP stream.")
        return

    state_message: MessageState = {"id": data_object.id, "state": StateEnum.STARTUP_PROCESS.value}
    await produce(state_message) 
    # КОРРЕКТНО ли так продьюсить стейт - как-то можно без await чтобы типо параллельно ?
    
    window_name = f"RTSP Stream {data_object.id}"  # Уникальное имя окна для каждого видео
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    while True:
        ret, frame = cap.read()
        if not ret:
            print('Error: No frame received from stream.')
            break

        cv2.imshow(window_name, frame)
        await asyncio.sleep(1) #нужен sleep видимо для передачи другому таску возможности его выполнить
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # КАК здесь сделать if пришло сообщение в топике стейт со стейтом "shutdown" - break + доп логика
        # consumer: AIOConsumer = get_runner_consumer()
        # await consumer.consume(controller.process)
    cap.release()
    cv2.destroyWindow(window_name)

    return 