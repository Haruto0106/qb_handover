from picamera2 import Picamera2

import cv2
import numpy as np
import time
from ultralytics import YOLO
import os
from queenbee.logger_drone import log_file_r, logger_info
from queenbee.bee import Bee
import asyncio

print("import complete")

class goalDetection:
    def __init__(self, coordinate):
        self.picam2 = Picamera2()
        self.picam2.resolution = (640,480)
        self.picam2.start()
        time.sleep(2)
        
        self.corrected_goal_coordinate = coordinate
        self.observed_goal_coordinate = [0.0,0.0,coordinate[2]]
        self.kalman_gain = 0.0
        
        self.theta_x = np.pi/4
        self.theta_y = np.pi/4
        
        self.model = YOLO('./last.pt')
   
    def take_photo(self):
        i = 0
        pic_dir = './log'+ log_file_r[:22]
        if not os.path.exists(pic_dir):
            os.mkdir(pic_dir)
        while True:
            self.pic_path = pic_dir + "/" + str(i).zfill(3)+".jpg"
            if os.path.exists(self.pic_path):
                # logger_info.info(self.pic_path + " already exists")
                i += 1
                continue
            else:
                break
        self.picam2.capture_file(self.pic_path)
    
    
    def predict(self):
        self.result = self.model(self.pic_path)
        for result in self.result:
            self.boxes = result.boxes
        
        return self.boxes
    
    async def detect_goal(self, drone:Bee):
        boxes = self.predict()
        try :
            boxes = boxes[0].xyxy
        except :
            # self.corrected_goal_coordinateにgoto
            await drone.Loop_goto_location(*self.corrected_goal_coordinate)
            return False
        
        self.picture_goal_coordinate =[]
        self.picture_goal_coordinate.append((boxes[0] + boxes[2])/2)
        self.picture_goal_coordinate.append((boxes[1] + boxes[3])/2)
        self.picture_goal_coordinate[0] = (self.picture_goal_coordinate[0]-320)/320
        self.picture_goal_coordinate[1] = (self.picture_goal_coordinate[1]-240)/240
        
        yaw_rad = 0.0174533* drone.Yaw_deg
        height = drone.Lidar
        
        Northern_distance = height * (np.tan(self.theta_x) * np.cos(yaw_rad)*self.picture_goal_coordinate[0] - np.tan(self.theta_y) * np.sin(yaw_rad)*self.picture_goal_coordinate[1])
        Eastern_distance  = height * (np.tan(self.theta_x) * np.sin(yaw_rad)*self.picture_goal_coordinate[0] + np.tan(self.theta_y) * np.cos(yaw_rad)*self.picture_goal_coordinate[1])
        
        # 地球を綺麗な球だと仮定する。半径はr＝6378100mである。北緯40°付近でぶった切ると半径はr=ｒ*cos(40°)。経度の差分に関しては  360 * Eastern_distance/(r*np.pi)。
        # 緯度に関して、360 * Northern_distance / (2 *6378100 *np.pi)
        # これとself.corrected_goal_coordinateを足したものを self.observed_goal_coordinateに格納する
        # カルマンフィルタで値を出して、self.corrected_goal_coordinateに格納して、goto
        
        r = 6378100
        self.defference_latitude  = 360 * Northern_distance / (2 *6378100 *np.pi)
        self.defference_longitude = 360 * Eastern_distance/(r * np.cos(40 * 0.0174533) * np.pi)
        
        
        self.corrected_goal_coordinate[0] = self.corrected_goal_coordinate[0] + self.defference_latitude
        self.corrected_goal_coordinate[1] = self.corrected_goal_coordinate[1] + self.defference_longitude
        
        await drone.Loop_goto_location(*self.corrected_goal_coordinate)
        return True
    
    async def precise_land(self,drone:Bee):
        is_goal = await self.detect_goal(drone)
        
        if is_goal :
            pass
        else :
            pass
    
        
cam = goalDetection([0,0,0])
cam.take_photo()
cam.predict()