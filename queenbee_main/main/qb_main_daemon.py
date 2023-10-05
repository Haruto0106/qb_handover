import spidev                       #SPI通信用のモジュールをインポート
import time                         #時間制御用のモジュールをインポート
import smbus
import RPi.GPIO as GPIO
import asyncio
import threading
import pandas as pd
from datetime import datetime, timedelta
from queenbee.class_case import Case
from omegaconf import OmegaConf
import sys
from queenbee.bee import Bee
from mavsdk.mission import MissionPlan, MissionItem
from queenbee.camera2 import Camera
from queenbee.lora_queenbee import Lora
import os

lst = ["matsudo", "arliss"]
condition = ""

##途中再起
path = "./condition.txt"
if os.path.isfile(path):
    with open(path,'r') as f:
        status = f.read()
else:
    status = "outside"
    print("outside")
    

def main_case(): ###Caseの関数
    global status
    if status == "outside":
        case_.judge_storage()
        with open(path,'w') as f:
            f.write("storage")
        status = "storage"
    if status == "storage":
        case_.judge_release()
        with open(path,'w') as f:
            f.write("release")
        status = "release"
    if status == "release":
        case_.judge_landing()
        with open(path,'w') as f:
            f.write("land")
        status = "land"
    if status == "land":
        case_.nichrome_on(case_.nichrome_stand, case_.nichrome_time)#これでケースのテグスを切るためのニクロム線が動作。テグス切れる
        case_.message = "Stand"
        time.sleep(10)
        case_.nichrome_on(case_.nichrome_arm, case_.nichrome_time)
        case_.message = "Expanded"
        case_.FINISHCASE = True
        with open(path,'w') as f:
            f.write("stand") 
                   

def main_run_case(): ###Caseのすべて
    thread1 = threading.Thread(target = main_case)
    thread2 = threading.Thread(target = case_.logger_push)
    if conf.lora:
        asyncio.run(lora.power_on())
        thread3 = threading.Thread(target = lora.cycle_send_progress2, args=[case_])
    thread1.start()
    thread2.start()
    if conf.lora:
        thread3.start()
    thread1.join()
    thread2.join()
    if conf.lora:
        thread3.join()
    #GPIO.cleanup()
    

async def main_flight():###Drone飛行の行程の関数
    global status
    if not status == "flying":                
        await asyncio.sleep(3)
        start = time.perf_counter()
        drone.lat_case = drone.Latitude_deg ###ケース座標
        drone.lon_case = drone.Longitude_deg
        altitude_home = drone.Absolute_altitude_m
        startpos = await drone.Precise_location(10)
        if conf.mode == "goto":
            await drone.Loop_arm_wait()
            if drone.Reboot_flag:
                return
            await drone.Set_takeoff_altitude(alt_target1 + 5)
            await drone.Takeoff() ### 浮上
            while drone.Lidar < alt_target1:
                await asyncio.sleep(0.01)    
            await drone.Hold()
            with open(path, "w") as f:
                f.write("flying")
            status = "flying"
        elif conf.mode == "mission":
            await drone.Clear_mission()
            await drone.Mission_append(latitude_target=startpos[0], ### 浮上
                                    longitude_target=startpos[1],
                                    altitude_target=alt_target1)
            await drone.Mission_append(latitude_target=lat_target1, ### ゴールへ移動
                                    longitude_target=lon_target1,
                                    altitude_target=alt_target1)
            mission_plan = MissionPlan(drone.Mission_items)
            await drone.mission.set_return_to_launch_after_mission(False)
            await drone.Upload_mission(mission_plan)
            await drone.Loop_hold_wait()
            if drone.Reboot_flag:
                return
            await drone.Loop_arm_wait()
            if drone.Reboot_flag:
                return
            await asyncio.sleep(1)
            await drone.Loop_mission_start()
            if drone.Reboot_flag:
                return
            with open(path,'w') as f:
                f.write("flying")
            status = "flying"
            
    if status == "flying":
        if conf.mode == "goto":
            await drone.Loop_goto_location_reboot(latitude_target=lat_target1, ### ゴールへ移動
                                            longitude_target=lon_target1,
                                            altitude_target=startpos[2] +alt_target1,
                                            start=start,
                                            reboot_time=reboot_time)
            if drone.Reboot_flag:
                return    
        elif conf.mode == "mission":
            while True:
                await asyncio.sleep(1)
                drone.Mission_finished = await drone.mission.is_mission_finished()
                if drone.Mission_finished:
                    logger_info.info("--mission finished")
                    if conf.lora:
                        await lora.write("--mission finished")
                    break
                if time.perf_counter() > start + reboot_time:
                    drone.Reboot_flag = True
                    return
                    
    await drone.Loop_hold_wait()
    if conf.camera:    
        await drone.Precise_land(camera=camera, time_out=precise_timeout, percent=percent)
        camera.close()
    # await drone.Land()
    await drone.Kill()
    logger_info.info("--finish")
    if conf.lora:
        await lora.write("--finish") 
    

async def main_drone():###Droneの全て,LoRaも
    await drone.Port_check()
    await drone.Connect()
    await drone.Catch_GPS()
    await drone.Loop_hold_wait()
    if drone.Reboot_flag:
        return
    if conf.lora:    
        await lora.power_on()
    await drone.Set_max_speed(speed=12)
    await drone.Set_speed(speed=10)
    drone.gotorange = conf.gotorange

    coroutines = [main_flight(),
                  drone.Loop_flight_mode(),
                  drone.Loop_position(),
                  drone.Loop_atitude(),
                  drone.Loop_lidar(),
                  drone.Loop_log(),
                  #drone.Loop_status_text() ###これがあるとデバッグしやすいが、リブート効かなくなるので、本番はコメントアウト
                ]
    if conf.mode == "mission":
        coroutines.extend([drone.Loop_mission_progress(),
                           drone.Loop_print_progress()
                           ])
    if conf.lora:
        coroutines.extend([lora.cycle_send_all_position(drone)
                           ])
    await asyncio.gather(*coroutines)
    
    if drone.Reboot_flag:
        await drone.Kill()
        await drone.Reboot()



### main #################################################################################
if __name__ == '__main__':
    ### 初期化 ################################################################
    from queenbee.logger_case import logger_info, log_format
    try:
        condition = sys.argv[1]
    except IndexError as e:
        logger_info.error(e)
        logger_info.info("条件未入力")
        exit()
        
    if condition in lst:
        if condition == "matsudo":
            with open("./config/matsudo_config.yaml", mode="r") as f:
                conf = OmegaConf.load(f)
        elif condition == "arliss" :
            with open("./config/arliss_config.yaml", mode="r") as f:
                conf = OmegaConf.load(f)
    else :
        logger_info.warning("--condition not specified")
        exit()
        
    if conf.case:
        case_ = Case()
        case_.nichrome_time = conf.nichrome_time
        case_.ligsen_rest_time = conf.ligsen_rest_time
        case_.presen_rest_time = conf.presen_rest_time
        case_.judge_storage_countmax = conf.judge_storage_countmax
        case_.judge_storage_maxtime = conf.judge_storage_maxtime
        case_.judge_storage_border_light = conf.judge_storage_border_light
        case_.judge_storage_sleep_time = conf.judge_storage_sleep_time
        case_.judge_release_lig_countmax = conf.judge_release_lig_countmax
        case_.judge_release_pre_countmax = conf.judge_release_pre_countmax
        case_.judge_release_maxtime = conf.judge_release_maxtime
        case_.judge_release_border_light = conf.judge_release_border_light
        case_.judge_release_disp_fore = conf.judge_release_disp_fore
        case_.judge_landing_countmax = conf.judge_landing_countmax
        case_.judge_landing_maxtime = conf.judge_landing_maxtime
        case_.pressure_tolerance = conf.pressure_tolerance
        case_.judge_landing_sleep_time = conf.judge_landing_sleep_time
    if conf.drone:
        SYSTEM_ADDRESS = conf.system_address
        lat_target1 = conf.target1.latitude
        lon_target1 = conf.target1.longitude
        alt_target1 = conf.target1.altitude
        precise_timeout = conf.precise_timeout
        reboot_time = conf.reboot_time
        percent = conf.percent
    if conf.camera:
        camera = Camera()
        camera.hlst = conf.hsv.h
        camera.slst = conf.hsv.s
        camera.vlst = conf.hsv.v
        camera.hlst2 = conf.hsv2.h
        camera.slst2 = conf.hsv2.s
        camera.vlst2 = conf.hsv2.v
    #     camera.shutter_speed = conf.photo.shutter_speed
    #     camera.framerate = conf.photo.framerate
    #     camera.exposure_mode = conf.photo.exposure_mode
    if conf.lora:
        lora = Lora()
        
    ###初期化がうまくいった事を、ハードで見て分かるような処理を入れたい(Lチカとか)
             
    ### 以下実行 ###########################################################################          
    if conf.case: ### ケース実行
        main_run_case()
        
    if conf.drone: ### ドローン実行
        while True:
            drone = Bee()
            del logger_info, log_format
            from queenbee.logger_drone import logger_info, log_format, log_file_r
            asyncio.run(main_drone())###これだめなん？ だめじゃないよ！ ここでエラーはいてるように見えるかもだけど、よく見たら、main関数の中でエラーはいてるはず!! 探せ！！！
            time.sleep(10)
    