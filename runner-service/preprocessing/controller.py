from .schema import MessageConsume, MessageState, StateEnum, ServiceSenderEnum
from producer import AIOProducer, get_state_producer, produce
from config import cfg
import cv2
from types import SimpleNamespace
import asyncio
from multiprocessing import Process
from multiprocessing import Event
from aiokafka import AIOKafkaConsumer
from .consumer import deserializer
from .processes_store import processes_store


async def process_shut_state(msg: MessageState, producer_state: AIOProducer):
    msg_obg: MessageState = SimpleNamespace(**msg)
    process_model = processes_store.get(str(msg_obg.id))

    if process_model and msg_obg.state == StateEnum.SHUTDOWN.value:
        custom_process = process_model.process
        custom_process.event.set()
        print(f"Process {msg_obg.id} stopped")
        await produce(producer_state, {"id" : msg_obg.id, "state" : StateEnum.INACTIVE_OK, "error": msg_obg.error, "sender": ServiceSenderEnum.RUNNER.value}) 
    
    elif not process_model:
        raise ValueError(f"Process not found for id {msg_obg.id}")
    return

async def consume_shutdown():
    state_consumer = AIOKafkaConsumer(
        cfg.state_topic,
        bootstrap_servers=f'{cfg.kafka_host}:{cfg.kafka_port}',
        value_deserializer=deserializer,
    )
    producer_state : AIOProducer = get_state_producer() 

    await state_consumer.start()
    print(f"Consumer state started\n")

    try:
        async for msg in state_consumer:
            msg_obg: MessageState = SimpleNamespace(**msg.value)
            if msg_obg.state == StateEnum.SHUTDOWN.value:
                await process_shut_state(msg.value, producer_state)
    finally:
        await state_consumer.stop()
        print(f"Consumer state stopped\n")
        await producer_state.stop()
        print(f"Producer state stopped\n")

    return





# async def process(message_consumed: MessageConsume):
#     print(f"Message {message_consumed} consumed")
#     data_object: MessageConsume = SimpleNamespace(**message_consumed)

#     cap = cv2.VideoCapture(data_object.rtsp_src)
#     if not cap.isOpened():
#         print("Error: Could not open RTSP stream.")
#         return

#     state_message: MessageState = {"id": data_object.id, "state": StateEnum.STARTUP_PROCESS.value}
#     await produce(state_message) 
#     # КОРРЕКТНО ли так продьюсить стейт - как-то можно без await чтобы типо параллельно ?
    
#     window_name = f"RTSP Stream {data_object.id}"  # Уникальное имя окна для каждого видео
#     cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             print('Error: No frame received from stream.')
#             break

#         cv2.imshow(window_name, frame)
#         await asyncio.sleep(1) #нужен sleep видимо для передачи другому таску возможности его выполнить
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#         # КАК здесь сделать if пришло сообщение в топике стейт со стейтом "shutdown" - break + доп логика
#         # consumer: AIOConsumer = get_runner_consumer()
#         # await consumer.consume(controller.process)
#     cap.release()
#     cv2.destroyWindow(window_name)

#     return 