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

    if process_model:
        custom_process = process_model.process
        custom_process.event.set()
        print(f"PROCESS {msg_obg.id} stopped")
        await produce(producer_state, {"id" : msg_obg.id, "state" : StateEnum.INACTIVE_OK, "error": msg_obg.error, "sender": ServiceSenderEnum.RUNNER.value}) 
        process_model.process.join()
        print("Is alive: ", processes_store.get(str(msg_obg.id)).process.is_alive())
        processes_store.pop(str(msg_obg.id))

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
            if msg_obg.state == StateEnum.SHUTDOWN.value and msg_obg.sender != ServiceSenderEnum.RUNNER.value:
                await process_shut_state(msg.value, producer_state)
    finally:
        await state_consumer.stop()
        print(f"Consumer state stopped\n")
        await producer_state.stop()
        print(f"Producer state stopped\n")

    return