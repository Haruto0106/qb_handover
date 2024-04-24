import cv2
import multiprocessing
print(1)
import numpy as np
print(2)
import time
print(3)
from ultralytics import YOLO
print(4)


def predict():
    print("start predict")
    starttime = time.time()
    model = YOLO('./runs/detect/train/weights/last.pt')
    model('test.jpg')
    endtime = time.time()
    print(endtime-starttime)

predict()
