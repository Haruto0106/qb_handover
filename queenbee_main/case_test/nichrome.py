import spidev                       #SPI通信用のモジュールをインポート
import time                         #時間制御用のモジュールをインポート
import smbus
import RPi.GPIO as GPIO
import asyncio
import threading
from queenbee.logger_case import logger_info, log_format

is_time_up = False
is_succeeded = False

GPIO.setmode(GPIO.BCM)
nichrome_pin_no_case = 23
nichrome_pin_no_stand = 25
nichrome_time =8

def nichrome_on(pin_no,t):
    GPIO.setup(pin_no, GPIO.OUT)#ピンを出力ピンに指定
    GPIO.output(pin_no, GPIO.HIGH)#これでニクロム線に電流が流れ始める。スイッチオン
    time.sleep(t)#t秒間継続
    GPIO.output(pin_no, GPIO.LOW)#これでニクロム線に電流が流れなくなる。スイッチオフ
    time.sleep(0.5)
    
        
    
if __name__ == "__main__":
    print("23start")
    nichrome_on(nichrome_pin_no_case, nichrome_time)
    print("10秒待機")
    time.sleep(10)
    print("25start")
    nichrome_on(nichrome_pin_no_stand, nichrome_time)
    print("fin")
    GPIO.cleanup()