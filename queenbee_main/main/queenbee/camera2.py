# import picamera
from picamera2 import Picamera2
import cv2
import numpy as np
import time
from queenbee.logger_drone import log_file_r, logger_info
import os
import datetime
import asyncio

class Camera(Picamera2):
# class Camera():
    def __init__(self):
        # LOG_DIR = os.path.abspath("log")
        # if not os.path.exists(LOG_DIR):
        #     os.makedirs(LOG_DIR)
        super().__init__()
        self.pic_path = ""
        self.height = 0.0
        self.width = 0.0
        self.percent = 0.0
        self.center = [0.0,0.0]
        self.y = 0.0
        self.x = 0.0
        
        self.detect = False
        
        self.tan_x = 500*4/3/650/2
        self.tan_y = 500/650/2
        
        self.hlst=[0, 0]
        self.slst=[0, 0]
        self.vlst=[0, 0]
        
        self.hlst2=[0, 0]
        self.slst2=[0, 0]
        self.vlst2=[0, 0]
        
        
        self.resolution = (640,480)
        
        logger_info.info('Camera initialized')
    
    # async def take_pic(self):
    #     i = 0
    #     pic_dir = './log'+ log_file_r[:22]
    #     if not os.path.exists(pic_dir):
    #         os.mkdir(pic_dir)
    #     while True:
    #         self.pic_path = pic_dir + "/" + str(i).zfill(3)+".jpg"
    #         if os.path.exists(self.pic_path):
    #             # logger_info.info(self.pic_path + " already exists")
    #             i += 1
    #             continue
    #         else:
    #             break
            
    #     self.resolution = (640,480)
    #     self.start_preview()
    #     self.capture(self.pic_path)
    async def take_pic(self):
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
        
        self.start()
        self.capture_file(self.pic_path)
        self.stop()

    async def save_detected_img(self, img, center_px):###重心位置に緑の円を描く
        cv2.circle(img, (int(center_px[0]), int(center_px[1])), 30, (0, 200, 0),
                thickness=3, lineType=cv2.LINE_AA)
        cv2.imwrite(self.pic_path, img)

    async def detect_center_cv(self):###赤の重心を探す
        img = cv2.imread(self.pic_path) # 画像を読み込む
        height, width = img.shape[:2] # 画像のサイズを取得する
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV_FULL) # 色基準で2値化する(HSVで色を表す)
        
        
        # 色の範囲を指定する
        hsv_min = np.array([self.hlst[0]*255/360, self.slst[0]*255/100, self.vlst[0]*255/100])
        hsv_max = np.array([self.hlst[1]*255/360, self.slst[1]*255/100, self.vlst[1]*255/100])
        mask = cv2.inRange(hsv, hsv_min, hsv_max)

        # 赤色のHSVの値域2　閾値が飛ぶ可能性を考慮
        hsv_min = np.array([self.hlst2[0]*255/360, self.slst2[0]*255/100, self.vlst2[0]*255/100])
        hsv_max = np.array([self.hlst2[1]*255/360, self.slst2[1]*255/100, self.vlst2[1]*255/100])
        mask2 = cv2.inRange(hsv, hsv_min, hsv_max)
        mask = mask + mask2

        # 非ゼロのピクセルが連続してできた領域を検出する
        nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask)

        #　画像の背景の番号は 0 とラベリングされているので、実際のオブジェクトの数は nlabels - 1 となる
        nlabels = nlabels - 1
        labels = np.delete(labels, obj=0, axis=0)
        stats = np.delete(stats, obj=0, axis=0)
        centroids = np.delete(centroids, obj=0, axis=0)
        centroids[:,0] = (width/2 - centroids[:,0]) / width*2
        centroids[:,1] = (height/2 - centroids[:,1]) / height*2
        percent = stats[:,4] / (height*width)
        
        if nlabels == 0:
            self.height = None
            self.width = None
            self.percent = 0
            self.center = None
            self.y = None
            self.x = None
            self.detect = False
        else:
            max_index = np.argmax(percent)
            self.height = height
            self.width = width
            self.percent = percent[max_index]
            self.center = centroids[max_index]
            self.y = centroids[max_index][1]
            self.x = centroids[max_index][0]
            self.detect = True
            await self.save_detected_img(img, ((1-self.center[0])*width/2, (1-self.center[1])*height/2))

    async def detect_center_ml():
        pass