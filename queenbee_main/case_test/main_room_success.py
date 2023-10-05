import spidev                       #SPI通信用のモジュールをインポート
import time                         #時間制御用のモジュールをインポート
import smbus
import RPi.GPIO as GPIO
import asyncio
import threading

is_time_up = False
is_succeeded = False

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
    #I2C設定
    i2c = smbus.SMBus(1)#SMBusの引数に1を指定する。Raspberry Piのi2cバスの番号(見た感じ引数1でよさそう)
    address = 0x5d
    print("i2c start")
    time.sleep(0.05)

    #Lセンサーの設定
    i2c.write_byte_data(address, 0x20, 0x90)
    time.sleep(0.05)
    print("sensor detected")
    
    
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
    print('Pressure: ' + str(prs))
    print('Temperature: ' + str(tmp))
    
    #一時停止
    time.sleep(0.05)
    return(prs)

def read_light():
    #SPI通信を行うための準備
    spi = spidev.SpiDev()               #インスタンスを生成
    spi.open(0, 0)                      #CE0(24番ピン)を指定
    spi.max_speed_hz = 1000000          #転送速度 1MHz

    #連続して値を読み込む
    while True:
        try:
            resp = spi.xfer2([0x68, 0x00])                 #SPI通信で値を読み込む
            volume = ((resp[0] << 8) + resp[1]) & 0x3FF    #読み込んだ値を10ビットの数値に変換
            time.sleep(1)                                  #1秒間待つ
            print(f"light sensor: {volume}")
            return volume
        except:
            continue


def read_disp_pressure():
     pre_1 = read_pressure()
     time.sleep(0.05)
     pre_2 = read_pressure()
     disp_pressure = pre_2 - pre_1
     print(f"absolute puressure: {pre_1}")
     print(f"disp pressure: {disp_pressure}")
     return(disp_pressure)

def read_altitude():
    alt = 0
    return alt

def read_disp_altitude():
    al_1 = read_altitude()
    time.sleep(3)
    al_2 = read_altitude()
    disp_altitude = al_2 - al_1
    return(disp_altitude)

"""
def start_timer():
    time_sta = time.perf_counter()
    return(time_sta)
"""

def read_timer(time_sta):
    time_end = time.perf_counter()# 時間計測終了
    tim = time_end - time_sta
    print(tim)
    return(tim)

def cut_line():
    return(0)

def judge_storage():
    global is_time_up
    light_counter = 0
    time_sta = time.perf_counter()

    while read_timer(time_sta) <= 300:
        if is_time_up:
            break

        time.sleep(0.5)
        if read_light() < 550:
                light_counter +=1
        else:
            light_counter = 0
            print("outside")

        if light_counter >= 10:
            break

    print("Storage Succeeded")
    return(True)

def judge_release():
    global is_time_up
    light_counter = 0
    pressure_counter = 0
    time_sta = time.perf_counter()

    while read_timer(time_sta) <= 300:
        if is_time_up:
            break

        if read_light() > 550:
                light_counter +=1
        elif light_counter < 10:
            light_counter = 0
            print("inside")

        if abs(read_disp_pressure()) > 0:
            pressure_counter +=1
            print(f"pressure_counter: {pressure_counter}")
        elif pressure_counter <10:
            pressure_counter =0
            print("failed")

        if light_counter >= 10 & pressure_counter >= 10:
            break

    print("Release Succeeded")
    return(True)

def judege_landing():
    global is_time_up
    pressure_tolerance = 0.13
    pressure_counter = 0
    time_sta = time.perf_counter()

    while read_timer(time_sta) <= 300:
        if is_time_up:
            break

        if abs(read_disp_pressure()) < pressure_tolerance:
            pressure_counter +=1
            print(f"pressure_counter: {pressure_counter}")
        elif pressure_counter <10:
            pressure_counter =0
            print("failed")
        if pressure_counter >= 10:
            break
        time.sleep(0.5)
    print("Landing Succeeded")
    return(True)


def nichrome_on(pin_no,t):
    GPIO.setup(pin_no, GPIO.OUT)#ピンを出力ピンに指定
    GPIO.output(pin_no, GPIO.HIGH)#これでニクロム線に電流が流れ始める。スイッチオン
    time.sleep(t)#t秒間継続
    GPIO.output(pin_no, GPIO.LOW)#これでニクロム線に電流が流れなくなる。スイッチオフ
    time.sleep(0.5)

def main():
    global is_succeeded
    judge_storage()
    judge_release()
    judege_landing()
    is_succeeded = True

    nichrome_on(nichrome_pin_no_case, nichrome_time)#これでケースのテグスを切るためのニクロム線が動作。テグス切れる
    time.sleep(10)
    nichrome_on(nichrome_pin_no_stand, nichrome_time)

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

if __name__ == '__main__':
    thread1 = threading.Thread(target=main)
    thread2 = threading.Thread(target=measure_time_up)
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    GPIO.cleanup()
