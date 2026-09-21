import cv2
from ultralytics import YOLO

model = YOLO("yolo26n.pt") 

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()

    if not ret:
        break

    results = model(frame, verbose=False)
    
    annotated_frame = results[0].plot()

    cv2.imshow("Camera", annotated_frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()