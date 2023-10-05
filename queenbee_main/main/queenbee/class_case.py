import spidev                       #SPI通信用のモジュールをインポート
import time                         #時間制御用のモジュールをインポート
import smbus
import RPi.GPIO as GPIO
import asyncio
from queenbee.logger_case import logger_info, log_format
import pandas as pd
from datetime import datetime, timedelta
from queenbee.bee import Bee

class Case():

    def __init__(self):

        logger_info.info("Case program initialized")
        self.STORAGE = False
        self.FINISHCASE = False
        self.CANUSEPRESSURE = True
        self.CANUSELIGHT = True
        GPIO.setmode(GPIO.BCM)

        self.nichrome_stand = 23
        self.nichrome_arm = 25

        #config#############################################

        self.nichrome_time = 0 
        self.ligsen_rest_time = 0
        self.presen_rest_time = 0

        self.judge_storage_countmax = 0
        self.judge_storage_maxtime = 0
        self.judge_storage_border_light = 0
        self.judge_storage_sleep_time = 0

        self.judge_release_lig_countmax = 0
        self.judge_release_pre_countmax = 0
        self.judge_release_maxtime = 0
        self.judge_release_border_light = 0
        self.judge_release_disp_fore = 0
        
        self.judge_landing_countmax = 0
        self.judge_landing_maxtime = 0
        self.pressure_tolerance = 0
        self.judge_landing_sleep_time = 0

        #通常変数###########################################

        self.pre = 0
        self.light = 0
        self.pre_disconnect = 0
        self.preerror = 0
        self.lighterror = 0
        self.ligsen_status_for_lora = "L"
        self.presen_status_for_lora = "L"
        self.disp_pressure = 0
        self.tim = 0
        self.phase = ""
        self.light_counter = 0
        self.message = ""
        self.pressure_counter = 0
        self.release_lst = []

    def read_light(self):#一度だけ光センサの値を読み取る
        #SPI通信を行うための準備
        spi = spidev.SpiDev()               #インスタンスを生成
        spi.open(0, 0)                      #CE0(24番ピン)を指定
        spi.max_speed_hz = 1000000          #転送速度 1MHz

        #連続して値を読み込む
        try:
            resp = spi.xfer2([0x68, 0x00])                 #SPI通信で値を読み込む
            self.light = ((resp[0] << 8) + resp[1]) & 0x3FF    #読み込んだ値を10ビットの数値に変換
            time.sleep(self.ligsen_rest_time)                                  #1秒間待つ
            # print(f"light sensor: {volume}")
            spi.close()

        except Exception as e:
            if self.lighterror > 5:
                self.CANUSELIGHT = False
                self.ligsen_status_for_lora = "D"
                logger_info.error(f"Light error:{e}")
                logger_info.info("Disabling light sensor")
                spi.close()
            
            else:
                self.light = 1
                self.lighterror += 1
                logger_info.error(f"Light error:{e}")
                spi.close()

        finally:
            time.sleep(self.ligsen_rest_time)
        
    # def read_pressure(self):
    #     try:
    #         #I2C設定
    #         i2c = smbus.SMBus(1)#SMBusの引数に1を指定する。Raspberry Piのi2cバスの番号(見た感じ引数1でよさそう)
    #         address = 0x5d
    #         time.sleep(0.02)

    #         #Lセンサーの設定
    #         i2c.write_byte_data(address, 0x20, 0x90)
    #         time.sleep(0.02)
            
    #         #データ読み込み
    #         pxl = i2c.read_byte_data(address, 0x28)
    #         pl = i2c.read_byte_data(address, 0x29)
    #         ph = i2c.read_byte_data(address, 0x2A)
    #         tl = i2c.read_byte_data(address, 0x2B)
    #         th = i2c.read_byte_data(address, 0x2C)
            
    #         #データ変換
    #         self.pre = ph << 16 | pl << 8 | pxl
    #         self.tmp = th << 8 | tl
            
    #         #極性判断(温度)
    #         if self.tmp >= 32768:
    #             self.tmp -= 65536
            
    #         #物理量に変換
    #         self.pre = self.pre / 4096
    #         self.tmp = 42.5 + self.tmp / 480
            
    #         #一時停止
    #         time.sleep(self.presen_rest_time)
        
    #     except Exception as e:
    #         logger_info.error(e)
    #         self.pre = 0 #これ危険
    #         self.tmp = 0


    def read_pressure(self):
        try:
            #I2C設定
            i2c = smbus.SMBus(1)#SMBusの引数に1を指定する。Raspberry Piのi2cバスの番号(見た感じ引数1でよさそう)
            address = 0x5d
            time.sleep(0.02)

            #Lセンサーの設定
            i2c.write_byte_data(address, 0x20, 0x90)
            time.sleep(0.02)
            
            #データ読み込み
            pxl = i2c.read_byte_data(address, 0x28)
            pl = i2c.read_byte_data(address, 0x29)
            ph = i2c.read_byte_data(address, 0x2A)
            tl = i2c.read_byte_data(address, 0x2B)
            th = i2c.read_byte_data(address, 0x2C)
            
            #データ変換
            self.pre = ph << 16 | pl << 8 | pxl
            self.tmp = th << 8 | tl
            
            #極性判断(温度)
            if self.tmp >= 32768:
                self.tmp -= 65536
            
            #物理量に変換
            self.pre = self.pre / 4096
            self.tmp = 42.5 + self.tmp / 480

            if self.pre == 0:
                self.pre_disconnect += 1
                if (self.pre_disconnect % 10 == 0):
                    logger_info.info("Pressure disconnected??")
                if self.pre_disconnect > 10:
                    self.CANUSEPRESSURE = False
                    self.presen_status_for_lora = "D"
                    logger_info.info("Disabling pressure sensor")
        
        except Exception as e:
            if self.preerror > 10:
                self.CANUSEPRESSURE = False
                self.presen_status_for_lora = "D"
                logger_info.error(f"Pressure error:{e}")
                logger_info.info("Disabling pressure sensor")
                
            else:
                self.pre = 1 #これ危険
                self.tmp = 1
                self.preerror += 1
                logger_info.error(f"Pressure error:{e}")

        finally:
            #一時停止
            time.sleep(self.presen_rest_time)

    def ave_pressure(self):
        pressure_lst = []
        for i in range(5):
            ### 多分ここにプレッシャーとる関数必要
            self.read_pressure()
            pressure_lst.append(self.pre)

            if i == 4:
                self.ave_pre = sum(pressure_lst)/len(pressure_lst)

    def disp_func_release(self):
         print("start")
         self.ave_pressure()
         avepre_before = self.ave_pre

         ### ここ1秒ラズパイを眠らせてよろしくて？能代仕様から戻す感じならこれで良き、arlissは滞空時間長いんで。でも松戸での試験考えるとよろしくないかも
         time.sleep(5)

         print("end")
         self.ave_pressure()
         avepre_after = self.ave_pre
         self.disp_pre = avepre_after - avepre_before

    def disp_func_land(self):
         print("start")
         self.ave_pressure()
         avepre_before = self.ave_pre

         ### ここ1秒ラズパイを眠らせてよろしくて？能代仕様から戻す感じならこれで良き、arlissは滞空時間長いんで。でも松戸での試験考えるとよろしくないかも
         time.sleep(3)

         print("end")
         self.ave_pressure()
         avepre_after = self.ave_pre
         self.disp_pre = avepre_after - avepre_before

    def read_timer(self,time_sta):
        time_end = time.perf_counter()# 時間計測終了
        self.tim = time_end - time_sta
        # print(tim)
        return self.tim
    
    def nichrome_on(self,pin_no,t):
        GPIO.setup(pin_no, GPIO.OUT)#ピンを出力ピンに指定
        GPIO.output(pin_no, GPIO.HIGH)#これでニクロム線に電流が流れ始める。スイッチオン
        logger_info.info("Cut case nichrome High")
        time.sleep(t)#t秒間継続
        GPIO.output(pin_no, GPIO.LOW)#これでニクロム線に電流が流れなくなる。スイッチオフ
        time.sleep(0.5)
        logger_info.info("Expanded nichrome Low")

    def logger_push(self):
        self.phase = "Outside"
        self.light=0
        self.pre=0
        self.disp_pre=0
        self.light_counter=0
        self.pressure_counter=0
        while True:
            while self.FINISHCASE == False:
                logger_info.info(log_format(
                    message = self.phase,
                    light = self.light,
                    pressure = self.pre,
                    disp_pressure = self.disp_pre,
                    light_counter = self.light_counter,
                    pressure_counter = self.pressure_counter
                ))
                time.sleep(1)
            return

    #収納判定
    def judge_storage(self):
        ##############################
        self.phase = "Outside"
        self.light_counter = 0 #counterを設定
        time_sta = time.perf_counter()
        ##############################
        while (self.read_timer(time_sta) <= self.judge_storage_maxtime):#300秒間実行

            if self.CANUSELIGHT == True:
                if self.light_counter < self.judge_storage_countmax:

                    self.read_light()

                    if self.light < self.judge_storage_border_light:#300以上であればcounterにプラス1
                        self.light_counter +=1
                        
                    else:
                        self.light_counter = 0#一回でも300以下であるならば外にいる判定
                        logger_info.info("Still Outside")
                        
                else:#10回連続で暗い判定ができたら中であると判定
                    break
            
            self.phase = "Judge Storage:" + self.ligsen_status_for_lora
            self.message = "JS:" + self.ligsen_status_for_lora + "," + str(self.light_counter)

            time.sleep(self.judge_storage_sleep_time)

        logger_info.info("Storage Succeeded")
        self.phase = "Storage"
        self.message = "Storage"
        self.STORAGE = True
        # return(True)

    # #放出判定松戸
    # def judge_release(self):
    #     ##############################
    #     self.light_counter = 0
    #     self.pressure_counter = 0
    #     time_sta = time.perf_counter()
    #     ##############################
    #     while (self.read_timer(time_sta) <= self.judge_release_maxtime):
    #         self.read_light()
    #         self.read_pressure()
    #         self.release_lst.append(self.pre)

    #         if self.light_counter < 10:
    #             if self.light > self.judge_release_border_light:#明るい判定が出たらcounterに+1
    #                 self.light_counter +=1
            
    #             else:#10回たまらないうちに暗い判定が出たらリセット
                
    #                 self.light_counter = 0

    #         if (self.light_counter > 5) and ((max(self.release_lst) - min(self.release_lst)) > 1):
    #             break

    #     logger_info.info("Release Succeeded")
    #     self.phase = "Released"
    #     self.message = "Released"

    
    #放出判定arliss
    def judge_release(self):
        ##############################
        self.light_counter = 0
        self.pressure_counter = 0
        time_sta = time.perf_counter()
        ##############################
        while (self.read_timer(time_sta) <= self.judge_release_maxtime):
            
            if self.CANUSELIGHT == False:
                self.light_counter = self.judge_release_lig_countmax
                time.sleep(5)

            if self.CANUSEPRESSURE == False:
                self.pressure_counter = self.judge_release_pre_countmax
                time.sleep(5)

            if (self.light_counter < self.judge_release_lig_countmax) and self.CANUSELIGHT == True:
                self.read_light()
                if self.light > self.judge_release_border_light:#明るい判定が出たらcounterに+1
                    self.light_counter +=1
            
                else:#10回たまらないうちに暗い判定が出たらリセット
                
                    self.light_counter = 0
                    logger_info.info("Light still low")


            if (self.pressure_counter < self.judge_release_pre_countmax) and self.CANUSEPRESSURE == True:
                self.disp_func_release()

                if self.disp_pre > self.judge_release_disp_fore:#pressureが変化していたら
                    self.pressure_counter +=1
                
            
                else:#10連続で変化を観測できなかったらリセット
                    self.pressure_counter = 0
                    logger_info.info("Disp pressure too stable or minus")
            
            if (self.light_counter >= self.judge_release_lig_countmax) and (self.pressure_counter >= self.judge_release_pre_countmax):
                break

            self.phase = "Judge Release:" + self.ligsen_status_for_lora + self.presen_status_for_lora
            self.message = "JR:" + self.ligsen_status_for_lora + self.presen_status_for_lora + "," + str(self.light_counter) + "," + str(self.pressure_counter)

            time.sleep(0.5)

        logger_info.info("Release Succeeded")
        self.phase = "Released"
        self.message = "Released"

    
    #着地判定
    def judge_landing(self):
        ##############################
        self.pressure_counter = 0
        time_sta = time.perf_counter()
        ##############################
        while (self.read_timer(time_sta) <= self.judge_landing_maxtime):
            
            if self.CANUSEPRESSURE == True:

                self.disp_func_land()
                
                if self.pressure_counter <= self.judge_landing_countmax:

                    if  (abs(self.disp_pre) < self.pressure_tolerance):
                        self.pressure_counter +=1

                    else:
                        self.pressure_counter =0
                        logger_info.info("Pressure not stable")

                else:
                    break

            self.phase = "Judge Land:" + self.presen_status_for_lora
            self.message = "JL:" + self.presen_status_for_lora + "," + str(self.pressure_counter)

            time.sleep(self.judge_landing_sleep_time)

        # print("Landing Succeeded")
        logger_info.info("Landing Succeeded")
        self.phase = "Land"
        self.message = "Land"
        # return(True)
