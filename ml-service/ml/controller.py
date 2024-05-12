from PIL import Image
from io import BytesIO
import numpy as np
from config import cfg
from minio_connection import s3
from . import db
from .models import DetectionDto
from .consumer import AIOKafkaConsumer, deserializer
from producer import AIOProducer, get_state_producer, produce
from .schema import MessageState, StateEnum, ServiceSenderEnum
from types import SimpleNamespace
from .processes_store import processes_store


async def upload_img_to_s3(img, filename):
    image = Image.fromarray(np.uint8(img))
    image_bytes = BytesIO()
    image.save(image_bytes, format='JPEG')
    image_bytes.seek(0)
    
    s3.put_object(
        cfg.minio_bucket,
        filename,
        image_bytes,
        length=len(image_bytes.getvalue()),
        content_type='image/jpeg'
    )

    s3_url = s3.presigned_get_object(bucket_name=cfg.minio_bucket, object_name=filename)
    return s3_url

async def save_detection_to_db(db_conn, s3_url, msg, result):
    new_row = DetectionDto(s3_url = s3_url, query_id = msg.id, 
                            detection_result = result.verbose()[:-2])
    await db.insert_new_row(db_conn, new_row)

async def process_shut_state(msg: MessageState, producer_state: AIOProducer):
    msg_obg: MessageState = SimpleNamespace(**msg)
    process_model = processes_store.get(str(msg_obg.id))

    if process_model and msg_obg.state == StateEnum.SHUTDOWN.value:
        custom_process = process_model.process
        custom_process.event.set()
        process_model.process.kill()
        print(f"Process {msg_obg.id} stopped")
        await produce(producer_state, {"id" : msg_obg.id, "state" : StateEnum.INACTIVE_OK, "error": msg_obg.error, "sender": ServiceSenderEnum.ML.value}) 
        
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
            if msg_obg.state == StateEnum.SHUTDOWN.value and msg_obg.sender != ServiceSenderEnum.ML.value:
                await process_shut_state(msg.value, producer_state)
    finally:
        await state_consumer.stop()
        print(f"Consumer state stopped\n")
        await producer_state.stop()
        print(f"Producer state stopped\n")

    return