import cv2
import numpy as np
import time
import os
from ultralytics import YOLO

import time
import picamera2.picamera2 as picamera

with picamera.Picamera2() as camera:
        camera.resolution = (640, 480)
        camera.start()
        time.sleep(2)
        camera.capture_file('test.jpg')

def predict():
    model = YOLO('./weights/last.pt')
    model('test.jpg',save=True, conf=0.2, iou=0.5)

predict()
