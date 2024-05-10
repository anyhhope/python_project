from aiokafka import AIOKafkaConsumer
from config import Config, cfg
import asyncio
import json
from typing import Callable
from .schema import MessageConsume
from types import SimpleNamespace
from .processes_store import processes_store
from .processes_store import ProcessModel
from .customProcess import CustomProcess

def deserializer(serialized):
    return json.loads(serialized)

class AIOConsumer():

    def __init__(self,  cfg: Config, consume_topic: str):
        self.__consumer = AIOKafkaConsumer(
            consume_topic,
            bootstrap_servers=f'{cfg.kafka_host}:{cfg.kafka_port}',
            value_deserializer=deserializer,
        )

        self.consume_topic = consume_topic

    async def start(self) -> None:
        await self.__consumer.start()

    async def stop(self) -> None:
        await self.__consumer.stop()

    async def consume(self):
        await self.start()
        print(f"Consumer started, topic: {self.consume_topic}\n")
        try:
            async for msg in self.__consumer:
                msg_object: MessageConsume = SimpleNamespace(**msg.value)
                process_model = processes_store.get(str(msg_object.id))
                print("GGGGGGGG", processes_store)
                print("ID", msg_object.id)
                if process_model:
                    print(f"Sending message to existing process for id {msg_object.id}")
                    process_model.process.send_message(msg_object)
                elif not process_model:
                    print("new process")
                    process = CustomProcess(id=msg_object.id)
                    processes_store[str(msg_object.id)] = ProcessModel(process_id=msg_object.id, process=process)
                    process.start()
                    process.send_message(msg_object)
        finally:
            await self.stop()
            print(f"Consumer stopped, topic: {self.consume_topic}\n")


        # if id_ in processes:
        #     # Если процесс существует для данного ID, отправляем сообщение на обработку
        #     print(f"Sending message {message} to existing process for id {id_}")
        #     processes[id_].send((id_, message))
        # else:
        #     # Если процесса нет, создаем новый
        #     print(f"Creating new process for id {id_}")
        #     process = Process(target=asyncio.run, args=(message_handler(id_, message),))
        #     process.start()
        #     processes[id_] = process


               