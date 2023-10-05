import spidev                       #SPI通信用のモジュールをインポート
import time                         #時間制御用のモジュールをインポート
import smbus
import RPi.GPIO as GPIO
import asyncio
import threading
from queenbee.logger_case import logger_info, log_format
from queenbee.bee import Bee
from queenbee.lora_case_queenbee import Lora
import pandas as pd
from datetime import datetime, timedelta
from class_case import Case
from omegaconf import OmegaConf
import sys


def main():
    global is_succeeded
    case_.judge_storage()
    case_.judge_release()
    case_.judge_landing()
    is_succeeded = True


    case_.nichrome_on(case_.nichrome_stand, case_.nichrome_time)#これでケースのテグスを切るためのニクロム線が動作。テグス切れる
    time.sleep(10)
    case_.nichrome_on(case_.nichrome_arm, case_.nichrome_time)
    lora.power_on()
    lora.cycle_send_position(drone)
    #lora.cycle_receive_lora(drone)


if __name__ == '__main__':#同時に処理を実行する
    case_ = Case()
    lora = Lora()
    drone = Bee()
    # condition = sys.argv[1]
    # match condition:
    #     case "room":
    with open("./config/room_case__config.yaml", mode="r") as f:
        conf = OmegaConf.load(f)
        # case "matsudo" :
        #     with open("config/matsudo_case__config.yaml", mode="r") as f:
        #         conf = OmegaConf.load(f)
        # case "honnbann" :
        #     with open("config/honnbann_case__config.yaml", mode="r") as f:
        #         conf = OmegaConf.load(f)
    case_.nichrome_time = conf.nichrome_time
    case_.setting_presen_time : conf.setting_presen_time
    case_.writing_presen_time : conf.writing_presen_time
    case_.presen_rest_time : conf.presen_rest_time
    case_.ligsen_rest_time : conf.ligsen_rest_time
    case_.judge_storage_maxtime : conf.judge_storage_maxtime
    case_.judge_storage_loop_time : conf.judge_storage_loop_time
    case_.judge_storage_border_light : conf.judge_storage_border_light
    case_.judge_release_maxtime : conf.judge_release_maxtime
    case_.judge_release_border_light : conf.judge_release_border_light
    case_.judge_landing_maxtime : conf.judge_landing_maxtime
    case_.judge_landing_sleep_time : conf.judge_landing_sleep_time
    case_.pressure_tolerance : conf.pressure_tolerance
    case_.maxmax_time : conf.maxmax_time
    thread1 = threading.Thread(target = main)
    thread2 = threading.Thread(target = case_.measure_time_up)
    thread3 = threading.Thread(target = case_.logger_push)
    thread1.start()
    thread2.start()
    thread3.start()
    thread1.join()
    thread2.join()
    thread3.join()

    GPIO.cleanup()
