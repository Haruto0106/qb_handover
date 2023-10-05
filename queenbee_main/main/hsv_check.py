import cv2
import numpy as np


file_name='.\\log\\2023-09-12_logger\\030\\000.jpg'

### h : 0-360  s: 0-100  v: 0-100


img=cv2.imread(file_name,cv2.IMREAD_COLOR)
# img=cv2.resize(img,(1000,600))
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV_FULL) # 色基準で2値化する(HSVで色を表す)
def click_pos(event, x, y, flags, params):
    if event == cv2.EVENT_MOUSEMOVE:
        img2=np.copy(img)
        cv2.circle(img2,center=(x,y),radius=5,color=(0,0,0),thickness=-1)
        h,s,v=hsv[y,x,:]
        hsv_str=f'(h,s,v)=({str(h*360/255)[:4]}, {str(s*100/255)[:4]}, {str(v*100/255)[:4]})'
        cv2.putText(img2,hsv_str,(30, 50),cv2.FONT_HERSHEY_PLAIN,2,(0,0,0),2,cv2.LINE_AA)
        cv2.imshow('window', img2)
        
cv2.imshow('window', img)
cv2.setMouseCallback('window', click_pos)
cv2.waitKey(0)
cv2.destroyAllWindows()