import cv2
from ultralytics import YOLO

model = YOLO("yolo26n-seg.pt") 

results = model(source = 0, show = True)