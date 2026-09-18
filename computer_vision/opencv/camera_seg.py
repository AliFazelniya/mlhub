import cv2
import sys
from ultralytics import YOLO
model = YOLO("yolov8n-seg.pt") 

s = 0
if len(sys.argv) > 1:
    arg = sys.argv[1]
    s = int(arg) if arg.isdigit() else arg

source = cv2.VideoCapture(s)

win_name = 'Camera Preview'
cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)

while True:
    has_frame, frame = source.read()
    if not has_frame:
        break

    results = model(frame, verbose=False)
    
    annotated_frame = results[0].plot()

    cv2.imshow(win_name, annotated_frame)

    if cv2.waitKey(1) == 27:
        break

source.release()
cv2.destroyAllWindows()