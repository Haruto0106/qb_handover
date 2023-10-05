import spidev                       #SPI通信用のモジュールをインポート
import time                         #時間制御用のモジュールをインポート
import smbus
import RPi.GPIO as GPIO
import asyncio
import threading
from queenbee.logger_case import logger_info, log_format
import pandas as pd
from datetime import datetime, timedelta

class Case():

    def __init__(self):
        logger_info.info("Case program initialized")
        self.is_time_up = False
        self.is_succeeded = False
        GPIO.setmode(GPIO.BCM)
        self.nichrome_stand = 23
        self.nichrome_arm = 25
        ####################################
        self.nichrome_time = None 
        self.setting_presen_time = None
        self.writing_presen_time = None
        self.presen_rest_time = None
        self.ligsen_rest_time = None
        self.judge_storage_maxtime = None
        self.judge_storage_loop_time = None
        self.judge_storage_border_light = None
        self.judge_release_maxtime = None
        self.judge_release_border_light = None
        self.judge_landing_maxtime = None
        self.judge_landing_sleep_time = None
        self.pressure_tolerance = None
        self.maxmax_time = None
        #######################################
        self.prs = None
        self.tmp = None
        self.volume = None
        self.pre_1 = None
        self.pre_2 = None
        self.disp_pressure = None
        self.tim = None
        self.phase = None
        self.light_counter = None
        self.pressure_counter = None
    """
    async def connect_to_drone():
        drone = Bee()
        # await drone.connect(system_address="udp://:14540")
        await drone.Connect(system_address="serial:///dev/ttyACM0:115200")
    """    
    # async def read_drone_pressure():
    #     return(0)

    def read_pressure(self):
        #I2C設定
        i2c = smbus.SMBus(1)#SMBusの引数に1を指定する。Raspberry Piのi2cバスの番号(見た感じ引数1でよさそう)
        address = 0x5d
        # print("i2c start")
        # logger_info.info("i2c start")
        time.sleep(self.setting_presen_time)

        #Lセンサーの設定
        i2c.write_byte_data(address, 0x20, 0x90)
        time.sleep(self.writing_presen_time)
        # print("sensor detected")
        # logger_info.info("sensor detected")
        
        
        #データ読み込み
        pxl = i2c.read_byte_data(address, 0x28)
        pl = i2c.read_byte_data(address, 0x29)
        ph = i2c.read_byte_data(address, 0x2A)
        tl = i2c.read_byte_data(address, 0x2B)
        th = i2c.read_byte_data(address, 0x2C)
        
        #データ変換
        self.prs = ph << 16 | pl << 8 | pxl
        self.tmp = th << 8 | tl
        
        #極性判断(温度)
        if self.tmp >= 32768:
            self.tmp -= 65536
        
        #物理量に変換
        self.prs = self.prs / 4096
        self.tmp = 42.5 + self.tmp / 480
        
        #表示
        # print('Pressure: ' + str(prs))
        # print('Temperature: ' + str(tmp))
        
        #一時停止
        time.sleep(self.presen_rest_time)
        return(self.prs)

    def read_light(self):
        #SPI通信を行うための準備
        spi = spidev.SpiDev()               #インスタンスを生成
        spi.open(0, 0)                      #CE0(24番ピン)を指定
        spi.max_speed_hz = 1000000          #転送速度 1MHz

        #連続して値を読み込む
        while True:
            try:
                resp = spi.xfer2([0x68, 0x00])                 #SPI通信で値を読み込む
                self.volume = ((resp[0] << 8) + resp[1]) & 0x3FF    #読み込んだ値を10ビットの数値に変換
                time.sleep(self.ligsen_rest_time)                                  #1秒間待つ
                # print(f"light sensor: {volume}")
                return self.volume
            except:
                continue


    def read_disp_pressure(self):
        self.pre_1 = self.read_pressure()
        time.sleep(0.05)
        self.pre_2 = self.read_pressure()
        self.disp_pressure = self.pre_2 - self.pre_1
        # print(f"absolute puressure: {pre_1}")
        # print(f"disp pressure: {disp_pressure}")
        return(self.disp_pressure)


    """
    def start_timer():
        time_sta = time.perf_counter()
        return(time_sta)
    """

    def read_timer(self,time_sta):
        time_end = time.perf_counter()# 時間計測終了
        self.tim = time_end - time_sta
        # print(tim)
        return(self.tim)

    def judge_storage(self):
        self.phase = "outside"
        self.light_counter = 0#counterを設定
        time_sta = time.perf_counter()

        while self.read_timer(time_sta) <= self.judge_storage_maxtime:#300秒間実行
            if self.is_time_up:
                break

            time.sleep(self.judge_storage_loop_time)
            if self.read_light() < self.judge_storage_border_light:#300以上であればcounterにプラス1
                    self.light_counter +=1
            else:
                self.light_counter = 0#一回でも300以下であるならば外にいる判定
                # print("outside")
                logger_info.info("outside")


            if self.light_counter >= 10:#10回連続で暗い判定ができたら中であると判定
                break

        # print("Storage Succeeded")
        logger_info.info("Storage Succeeded")
        self.phase = "Storage"

        return(True)

    def judge_release(self):
        self.light_counter = 0
        self.pressure_counter = 0
        time_sta = time.perf_counter()

        while self.read_timer(time_sta) <= self.judge_release_maxtime:
            if self.is_time_up:
                break

            if self.read_light() > self.judge_release_border_light:#明るい判定が出たらcounterに+1
                    self.light_counter +=1
            elif self.light_counter < 10:#10回たまらないうちに暗い判定が出たらリセット
                self.light_counter = 0
                # print("inside")
                # logger_info.info("Storage")
                
            if self.read_disp_pressure() > 0:#pressureが変化していたら
                self.pressure_counter +=1
                # print(f"pressure_counter: {pressure_counter_release}")
            elif self.pressure_counter <10:#10連続で変化を観測できなかったらリセット
                self.pressure_counter =0
                # print("failed")
                # logger_info.info("failed")
            if self.light_counter >= 10 and self.pressure_counter >= 10:
            #if self.light_counter >= 10 :
                break

        # print("Release Succeeded")
        logger_info.info("Release Succeeded")
        self.phase = "Released"
        return(True)

    def judge_landing(self):
        #self.pressure_tolerance = 0.15#今見た感じ風も考慮して0.15に変えた、、結構変わる
        self.pressure_counter = 0
        time_sta = time.perf_counter()

        while self.read_timer(time_sta) <= self.judge_landing_maxtime:
            if self.is_time_up:
                break
            if self.read_disp_pressure() < self.pressure_tolerance:
                self.pressure_counter +=1
                # print(f"pressure_counter: {pressure_counter}")
            elif self.pressure_counter <10:
                self.pressure_counter =0
                # print("failed")
                logger_info.info("failed")
            if self.pressure_counter >= 10:
                break
            time.sleep(self.judge_landing_sleep_time)
        # print("Landing Succeeded")
        logger_info.info("Landing Succeeded")
        self.phase = "Land"
        return(True)


    def nichrome_on(self,pin_no,t):
        GPIO.setup(pin_no, GPIO.OUT)#ピンを出力ピンに指定
        GPIO.output(pin_no, GPIO.HIGH)#これでニクロム線に電流が流れ始める。スイッチオン
        logger_info.info("Cut case")
        time.sleep(t)#t秒間継続
        GPIO.output(pin_no, GPIO.LOW)#これでニクロム線に電流が流れなくなる。スイッチオフ
        logger_info.info("Begin expantion")
        time.sleep(0.5)
        logger_info.info("Expanded")

    # def lst_pressure():
    #     global timelst
    #     global pressurelst
    #     while True:
    #         timelst = []
    #         pressurelst = []
    #         #df = pd.read_csv(r'.\\log\\2023-06-18_logger\\007.csv')
    #         df = pd.read_csv('./log/2023-06-18_logger/007.csv')
    #         for i in range(len(df)):
    #             if df.iloc[i]['Message'] == 'Released' or df.iloc[i]['Message'] == 'Land':
    #                 timelst.append(datetime.strptime(str(df.iloc[i]['Timeinfo'])[:19], '%Y-%m-%d %H:%M:%S'))
    #                 pressurelst.append(df.iloc[i]['Pressure'])
    #         time.sleep(2)

    # def lst_storage_light():
    #     global timelst
    #     global lightlst
    #     timelst = []
    #     lightlst = []
    #     #df = pd.read_csv(r'.\\log\\2023-06-18_logger\\007.csv')
    #     df = pd.read_csv('./log/2023-06-18_logger/007.csv')
    #     for i in range(len(df)):
    #         if df.iloc[i]['Message'] == 'Unstored':
    #             timelst.append(datetime.strptime(str(df.iloc[i]['Timeinfo'])[:19], '%Y-%m-%d %H:%M:%S'))
    #             lightlst.append(df.iloc[i]['Light'])
    #     time.sleep(2)


    def measure_time_up(self):
        time_sta = time.time()
        while self.is_succeeded == False:
            time.sleep(5)
            if (time.time() - time_sta) > self.maxmax_time:
                self.is_time_up = True
                break
        return(True)

    def logger_push(self):
        self.phase = "Outside"
        self.pre_1 = 0
        self.disp_pressure = 0
        self.volume = 0
        self.tmp = 0
        self.pressure_counter = 0
        self.light_counter = 0
        
        while True:
            logger_info.info(log_format(
                message=self.phase,
                light=self.volume,
                light_counter=self.light_counter,
                pressure=self.pre_1,
                disp_pressure=self.disp_pressure,
                pressure_counter=self.pressure_counter,
                temperature=self.tmp
            ))
            time.sleep(1)