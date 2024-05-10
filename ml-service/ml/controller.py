from ultralytics import YOLO
from PIL import Image
import base64
from io import BytesIO
import numpy as np
from config import cfg
from minio_connection import s3
from data import Database, PoolConnectionProxy, get_connection
from . import db
from models import DetectionDto
from .consumer import AIOKafkaConsumer, deserializer
from producer import AIOProducer, get_state_producer, produce
from schema import MessageState, StateEnum, ServiceSenderEnum
from types import SimpleNamespace
from .processes_store import processes_store


async def process(msg):
    model = YOLO('./yolo_model/yolov9c.pt')
    img_bytes = base64.b64decode(msg['frame'])
    img = Image.open(BytesIO(img_bytes))


    results = model([img]) 

    # Process results list
    for result in results:
        boxes = result.boxes  # Boxes object for bounding box outputs
        masks = result.masks  # Masks object for segmentation masks outputs
        keypoints = result.keypoints  # Keypoints object for pose outputs
        probs = result.probs  # Probs object for classification outputs
        obb = result.obb  # Oriented boxes object for OBB outputs
        result.show()  # display to screen
        result.save(filename='result.jpg')  # save to disk
    return 


async def upload_img_to_s3(img, filename):
    image = Image.fromarray(np.uint8(img))
    image_bytes = BytesIO()
    image.save(image_bytes, format='JPEG')
    image_bytes.seek(0)
    
    # filename = f"frame_{msg.id}_{msg.frame_id}.jpg"
    s3.put_object(
        cfg.minio_bucket,
        filename,
        image_bytes,
        length=len(image_bytes.getvalue()),
        content_type='image/jpeg'
    )

    s3_url = s3.presigned_get_object(bucket_name=cfg.minio_bucket, object_name=filename)
    return s3_url

async def save_detection_to_db(s3_url, msg, result):
    db_instance = Database(cfg)
    await db_instance.connect()
    new_row = DetectionDto(s3_url = s3_url, query_id = msg.id, 
                            detection_result = result.verbose()[:-2])
    db_conn: PoolConnectionProxy = await get_connection(db_instance)
    await db.insert_new_row(db_conn, new_row)

async def process_shut_state(msg: MessageState, producer_state: AIOProducer):
    msg_obg: MessageState = SimpleNamespace(**msg)
    process_model = processes_store.get(str(msg_obg.id))

    if process_model and msg_obg.state == StateEnum.SHUTDOWN.value:
        custom_process = process_model.process
        custom_process.event.set()
        print(f"Process {msg_obg.id} stopped")
        await produce(producer_state, {"id" : msg_obg.id, "state" : StateEnum.INACTIVE_OK, "error": msg_obg.error, "sender": ServiceSenderEnum.ML.value}) 
    
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
            await process_shut_state(msg.value, producer_state)
    finally:
        await state_consumer.stop()
        print(f"Consumer state stopped\n")
        await producer_state.stop()
        print(f"Producer state stopped\n")

    return