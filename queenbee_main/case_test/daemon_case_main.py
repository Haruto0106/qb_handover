import spidev                       #SPI通信用のモジュールをインポート
import time                         #時間制御用のモジュールをインポート
import smbus
import RPi.GPIO as GPIO
import asyncio
import threading
from queenbee.logger_case import logger_info, log_format
import pandas as pd
from datetime import datetime, timedelta

is_time_up = False
is_succeeded = False
path = "./condition.txt"


GPIO.setmode(GPIO.BCM)
nichrome_pin_no_case = 23
nichrome_pin_no_stand = 25
nichrome_time = 5
"""
async def connect_to_drone():
    drone = Bee()
    # await drone.connect(system_address="udp://:14540")
    await drone.Connect(system_address="serial:///dev/ttyACM0:115200")
"""    
async def read_drone_pressure():
    return(0)


    
def read_pressure():
    global tmp
    #I2C設定
    i2c = smbus.SMBus(1)#SMBusの引数に1を指定する。Raspberry Piのi2cバスの番号(見た感じ引数1でよさそう)
    address = 0x5d
    # print("i2c start")
    # logger_info.info("i2c start")
    time.sleep(0.05)

    #Lセンサーの設定
    i2c.write_byte_data(address, 0x20, 0x90)
    time.sleep(0.05)
    # print("sensor detected")
    # logger_info.info("sensor detected")
    
    
    #データ読み込み
    pxl = i2c.read_byte_data(address, 0x28)
    pl = i2c.read_byte_data(address, 0x29)
    ph = i2c.read_byte_data(address, 0x2A)
    tl = i2c.read_byte_data(address, 0x2B)
    th = i2c.read_byte_data(address, 0x2C)
    
    #データ変換
    prs = ph << 16 | pl << 8 | pxl
    tmp = th << 8 | tl
    
    #極性判断(温度)
    if tmp >= 32768:
        tmp -= 65536
    
    #物理量に変換
    prs = prs / 4096
    tmp = 42.5 + tmp / 480
    
    #表示
    # print('Pressure: ' + str(prs))
    # print('Temperature: ' + str(tmp))
    
    #一時停止
    time.sleep(0.05)
    return(prs)

def read_light():
    global volume
    #SPI通信を行うための準備
    spi = spidev.SpiDev()               #インスタンスを生成
    spi.open(0, 0)                      #CE0(24番ピン)を指定
    spi.max_speed_hz = 1000000          #転送速度 1MHz

    #連続して値を読み込む
    while True:
        try:
            resp = spi.xfer2([0x68, 0x00])                 #SPI通信で値を読み込む
            volume = ((resp[0] << 8) + resp[1]) & 0x3FF    #読み込んだ値を10ビットの数値に変換
            time.sleep(0.05)                                  #1秒間待つ
            # print(f"light sensor: {volume}")
            return volume
        except:
            continue


def read_disp_pressure():
    global disp_pressure
    global pre_1
    pre_1 = read_pressure()
    time.sleep(0.05)
    pre_2 = read_pressure()
    disp_pressure = pre_2 - pre_1
    # print(f"absolute puressure: {pre_1}")
    # print(f"disp pressure: {disp_pressure}")
    return(disp_pressure)


"""
def start_timer():
    time_sta = time.perf_counter()
    return(time_sta)
"""

def read_timer(time_sta):
    time_end = time.perf_counter()# 時間計測終了
    tim = time_end - time_sta
    # print(tim)
    return(tim)

def judge_storage():
    global phase
    phase = "outside"
    global is_time_up
    global light_counter
    light_counter = 0#counterを設定
    time_sta = time.perf_counter()

    while read_timer(time_sta) <= 300:#300秒間実行
        if is_time_up:
            break

        time.sleep(0.5)
        if read_light() < 550:#300以上であればcounterにプラス1
                light_counter +=1
        else:
            light_counter = 0#一回でも300以下であるならば外にいる判定
            # print("outside")
            logger_info.info("outside")


        if light_counter >= 10:#10回連続で暗い判定ができたら中であると判定
            break

    # print("Storage Succeeded")
    logger_info.info("Storage Succeeded")
    phase = "Storage"

    return(True)

def judge_release():
    global phase
    global is_time_up
    global light_counter
    global pressure_counter
    light_counter = 0
    pressure_counter = 0
    time_sta = time.perf_counter()

    while read_timer(time_sta) <= 300:
        if is_time_up:
            break

        if read_light() > 550:#明るい判定が出たらcounterに+1
                light_counter +=1
        elif light_counter < 10:#10回たまらないうちに暗い判定が出たらリセット
            light_counter = 0
            # print("inside")
            # logger_info.info("Storage")
            
        if read_disp_pressure() > 0:#pressureが変化していたら
            pressure_counter +=1
            # print(f"pressure_counter: {pressure_counter_release}")
        elif pressure_counter <10:#10連続で変化を観測できなかったらリセット
            pressure_counter =0
            # print("failed")
            # logger_info.info("failed")
        # if light_counter >= 10 & pressure_counter >= 10:
        if light_counter >= 10 :
            break

    # print("Release Succeeded")
    logger_info.info("Release Succeeded")
    phase = "Released"
    return(True)

def judge_landing():
    global phase
    global is_time_up
    pressure_tolerance = 0.15#今見た感じ風も考慮して0.15に変えた、、結構変わる
    global pressure_counter
    pressure_counter = 0
    time_sta = time.perf_counter()

    while read_timer(time_sta) <= 300:
        if is_time_up:
            break
        if read_disp_pressure() < pressure_tolerance:
            pressure_counter +=1
            # print(f"pressure_counter: {pressure_counter}")
        elif pressure_counter <10:
            pressure_counter =0
            # print("failed")
            logger_info.info("failed")
        if pressure_counter >= 10:
            break
        time.sleep(1)
    # print("Landing Succeeded")
    logger_info.info("Landing Succeeded")
    phase = "Land"
    return(True)


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

def main(progress):
    # progress 
    # 0 ⇒何もなし 最初から実行
    # 1⇒収納判定完了 放出判定から
    # 2⇒放出判定完了 着地判定から
    # 3⇒着地判定完了 展開から

    global is_succeeded


    if progress == 0:
        judge_storage()
        with open(path,'w') as f:
            f.write("1")
    
    if progress == 0 or progress == 1:
        judge_release()
        with open(path,'w') as f:
            f.write("11")

    if progress == 0 or progress == 1 or progress == 2:
        judge_landing()
        with open(path,'w') as f:
            f.write("111")
        is_succeeded = True

    nichrome_on(nichrome_pin_no_case, nichrome_time)#これでケースのテグスを切るためのニクロム線が動作。テグス切れる
    time.sleep(10)
    nichrome_on(nichrome_pin_no_stand, nichrome_time)
    with open(path,'w') as f:
        f.write("1111")


def measure_time_up():
    global is_succeeded
    global is_time_up
    time_sta = time.time()
    while is_succeeded == False:
        time.sleep(5)
        if (time.time() - time_sta) > 120:
            is_time_up = True
            break
    return(True)

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
            tempreture=tmp
        ))
        time.sleep(1)
    
    

if __name__ == '__main__':#同時に処理を実行する
    with open(path,'r') as f:
        progress = len(f.read())

    if progress >= 4:
        progress = 0
        f = open(path,"w")
        f.close()

    
    thread1 = threading.Thread(target = main, args = (progress,))
    thread2 = threading.Thread(target = measure_time_up)
    thread3 = threading.Thread(target = logger_push)
    thread1.start()
    thread2.start()
    thread3.start()
    thread1.join()
    thread2.join()
    thread3.join()

    GPIO.cleanup()