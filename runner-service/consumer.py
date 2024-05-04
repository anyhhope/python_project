from aiokafka import AIOKafkaConsumer
from config import Config, cfg
import asyncio
import json
from typing import Callable

def deserializer(serialized):
    return json.loads(serialized)

class AIOConsumer():

    def __init__(self,  cfg: Config, consume_topic: str):
        self.__consumer = AIOKafkaConsumer(
            consume_topic,
            bootstrap_servers=f'{cfg.kafka_host}:{cfg.kafka_port}',
            value_deserializer=deserializer,
        )

    async def start(self) -> None:
        await self.__consumer.start()

    async def stop(self) -> None:
        await self.__consumer.stop()

    async def consume(self, event_handler: Callable[..., None]):
        await self.start()
        print("Consumer started")
        tasks = []
        try:
            async for msg in self.__consumer:
                tasks.append(asyncio.create_task(event_handler(msg.value)))
        finally:
            await self.stop()
            print("Consumer stopped")
        await asyncio.gather(*tasks)



               