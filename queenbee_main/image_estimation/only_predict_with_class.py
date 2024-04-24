import cv2
import numpy as np
import time
from ultralytics import YOLO
print("import completed")

class goalDetection():
    def __init__(self):
        self.corrected_goal_coordinate = [0.0,0.0,0.0]
        self.observed_goal_coordinate = [0.0,0.0,0.0]
        self.kalman_gain = 0.0
        
        self.model = YOLO('./last.pt')
    
    def predict(self,path):
        self.result = self.model(path,save=True)
        for result in self.result:
            self.boxes = result.boxes
        
        return self.boxes
    
    def goal_detection(self,path):
        boxes = self.predict(path)
        try :
            boxes = boxes[0].xyxy[0]
            print(boxes[0])
        except :
            print("error")

goal = goalDetection()
goal.goal_detection("black.png")
goal.goal_detection("test.jpg")
goal.goal_detection("desert.jpg")