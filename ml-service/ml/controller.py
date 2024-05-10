from ultralytics import YOLO



async def process(msg):
    model = YOLO('./yolo_model/yolov9c.pt')

    results = model(['im1.jpg'])  # return a list of Results objects

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