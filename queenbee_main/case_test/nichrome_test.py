import spidev                       #SPI通信用のモジュールをインポート
import time                         #時間制御用のモジュールをインポート
import smbus
import RPi.GPIO as GPIO
import asyncio
import threading
from queenbee.logger_case import logger_info, log_format
import pandas as pd
from datetime import datetime, timedelta
import time

GPIO.setmode(GPIO.BCM)
nichrome_stand = 23
nichrome_arm = 25
nichrome_time = 5

def nichrome_on(pin_no,t):
    global phase
    GPIO.setup(pin_no, GPIO.OUT)#ピンを出力ピンに指定
    GPIO.output(pin_no, GPIO.HIGH)#これでニクロム線に電流が流れ始める。スイッチオン
    logger_info.info("Cut case")
    time.sleep(t)#t秒間継続
    GPIO.output(pin_no, GPIO.LOW)#これでニクロム線に電流が流れなくなる。スイッチオフ
    logger_info.info("Begin expantion")
    time.sleep(0.5)
    logger_info.info("Expanded")

def searchssh():
    i = 0
    while True:
        i = i + 0.5
        time.sleep(0.5)
        print(i)

def nichrome():
    nichrome_on(nichrome_stand, nichrome_time)#これでケースのテグスを切るためのニクロム線が動作。テグス切れる
    time.sleep(3)
    nichrome_on(nichrome_arm, nichrome_time)
    GPIO.cleanup()
    i = 0
    while True:
        i = i + 0.5
        time.sleep(0.5)
        print(i)

def logger_push():
    global phase
    phase = "Outside"
    global pre_1
    pre_1 = 0
    global disp_pressure
    disp_pressure = 0
    global volume
    volume = 0
    global tmp
    tmp = 0
    global pressure_counter
    pressure_counter = 0
    global light_counter
    light_counter = 0
    
    while True:
        logger_info.info(log_format(
            message=phase,
            light=volume,
            light_counter=light_counter,
            pressure=pre_1,
            disp_pressure=disp_pressure,
            pressure_counter=pressure_counter,
            temperature=tmp
        ))
        time.sleep(1)

if __name__ == '__main__':#同時に処理を実行する
    thread1 = threading.Thread(target=searchssh)
    thread2 = threading.Thread(target=logger_push)
    thread3 = threading.Thread(target=nichrome)
    thread1.start()
    thread2.start()
    thread3.start()
    thread1.join()
    thread2.join()
    thread3.join()
