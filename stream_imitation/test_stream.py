import cv2

rtsp_url = "rtsp://fake.kerberos.io/stream"

# Создаем объект VideoCapture для чтения RTSP потока
cap = cv2.VideoCapture(rtsp_url)

# Проверяем, открылся ли поток
if not cap.isOpened():
    print("Error: Could not open RTSP stream.")
    exit()

# Цикл для чтения и отображения кадров из RTSP потока
while True:
    ret, frame = cap.read()
    if not ret:
        print('Error: No frame received from stream.')
        break

    # Отображаем кадр
    cv2.imshow("RTSP Stream", frame)

    # Проверяем нажатие клавиши 'q' для выхода из цикла
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Освобождаем объект VideoCapture и закрываем все окна OpenCV
cap.release()
cv2.destroyAllWindows()
