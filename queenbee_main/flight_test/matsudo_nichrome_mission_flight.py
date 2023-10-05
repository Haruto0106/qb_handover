#!/usr/bin/env python3

import time
import RPi.GPIO as GPIO

import asyncio
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan
from queenbee.bee import Bee
from queenbee.logger_drone import logger_info, log_file_r
from queenbee.plotter import df_lidar, plot_lidar, df_GPS, plot_GPS, plot_position, map_GPS

SYSTEMADDRESS = "serial:///dev/ttyACM0:115200"
altitude_start=3

# latitude_start=35.7963106###松戸の橋の座標
# longitude_start=139.89165

# latitude_start = 35.715556
# longitude_start = 139.760441

# latitude_goal = 35.796723   #ゲートボール場の座標 
# longitude_goal = 139.8918259

# latitude_goto = 0.0003
# longitude_goto = 0.0003

latitude_goal = 35.7968762 # ゲートボール真ん中
longitude_goal = 139.8918651



GPIO.setmode(GPIO.BCM)
nichrome_pin_no_case = 23
nichrome_pin_no_stand = 25
nichrome_time = 8

def nichrome_on(pin_no,t):
    GPIO.setup(pin_no, GPIO.OUT)#ピンを出力ピンに指定
    GPIO.output(pin_no, GPIO.HIGH)#これでニクロム線に電流が流れ始める。スイッチオン
    time.sleep(t)#t秒間継続
    GPIO.output(pin_no, GPIO.LOW)#これでニクロム線に電流が流れなくなる。スイッチオフ
    time.sleep(0.5)


async def run():
    await drone.Connect(system_address=SYSTEMADDRESS)
    await drone.Catch_GPS()
        
    coroutines = [
        main_run(),
        drone.Loop_flight_mode(),
        drone.Loop_position(),
        drone.Loop_lidar(),
        drone.Loop_mission_progress(),
        drone.Loop_log(),
        drone.Loop_status_text(),
        drone.Loop_mission_progress(),
        ]
    await asyncio.gather(*coroutines)

async def main_run():
    await asyncio.sleep(2)
    latitude_start = drone.Latitude_deg
    longitude_start = drone.Longitude_deg
    mission_items = []
    mission_items.append(MissionItem(latitude_start,
                                     longitude_start,
                                     altitude_start,
                                     0,
                                     False,
                                     float('nan'),
                                     float('nan'),
                                     MissionItem.CameraAction.NONE,
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     float('nan')))
    mission_items.append(MissionItem(latitude_goal,
                                    longitude_goal,
                                    altitude_start,
                                    0,
                                    False,
                                    float('nan'),
                                    float('nan'),
                                    MissionItem.CameraAction.NONE,
                                    float('nan'),
                                    float('nan'),
                                    float('nan'),
                                    float('nan'),
                                    float('nan')))
    mission_plan = MissionPlan(mission_items)
    await drone.mission.set_return_to_launch_after_mission(False)
    await drone.Upload_mission(mission_plan)
    
    await drone.Loop_hold_wait(system_address=SYSTEMADDRESS)
    
    await drone.Arm()
    
    await asyncio.sleep(5)
    await drone.Start_mission()
    while True:
        await asyncio.sleep(1)
        mission_finished = await drone.mission.is_mission_finished()
        if mission_finished:
            logger_info.info("--mission finished")
            break        
    await drone.Land()
    await asyncio.sleep(10)

        
if __name__ == "__main__":
    print("stand start")
    nichrome_on(nichrome_pin_no_case, nichrome_time)
    print("7.5秒待機")
    time.sleep(7.5)
    print("arm start")
    nichrome_on(nichrome_pin_no_stand, nichrome_time)
    print("fin")
    GPIO.cleanup()
    time.sleep(10)
    print("10秒待機")


    drone = Bee()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())