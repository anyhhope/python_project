from ultralytics import YOLO
from PIL import Image
import base64
from io import BytesIO


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