#!/usr/bin/env python3
import asyncio
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan
from queenbee.bee import Bee
from queenbee.logger_drone import logger_info, log_file_r
import numpy as np
import time
from numpy import linalg as la
import random
from queenbee.camera import Camera
# from queenbee.plotter import df_lidar, plot_lidar, df_GPS, plot_GPS, plot_position, map_GPS
SYSTEMADDRESS = "serial:///dev/ttyACM0:115200"
altitude_hover=3
altitude_goto = 3

latitude_goal = 35.7926509   #畑横の座標
longitude_goal = 139.8908180

alpha = np.pi/4

Cir_eq = 40076500 #m
Cir_md = 40008600 #m

time_fin = 180

KP = 0
KI = 0
KD = 0

async def run():
    await drone.Connect(system_address=SYSTEMADDRESS)
    await drone.Catch_GPS()
    await drone.Loop_hold_wait(system_address=SYSTEMADDRESS)
      
    coroutines = [
        main_run(),
        drone.Loop_flight_mode(),
        drone.Loop_position(),
        drone.Loop_lidar(),
        drone.Loop_mission_progress(),
        drone.Loop_log(),
        drone.Loop_status_text(),
        drone.Loop_mission_progress(),
        drone.Loop_atitude()
        ]
    await asyncio.gather(*coroutines)



async def main_run():
    await asyncio.sleep(2)
    await drone.Arm()
    latitude_start = drone.Latitude_deg
    longitude_start = drone.Longitude_deg
    altitude_home = drone.Absolute_altitude_m
    altitude_goal = altitude_home + altitude_goto
    
    
    await drone.Set_takeoff_altitude(5)
    await drone.Takeoff()
    while drone.Lidar <= 3:
        await asyncio.sleep(0.05)
    
    await drone.Loop_goto_location(latitude_target=latitude_goal,
                                   longitude_target=longitude_goal,
                                   altitude_target=drone.Absolute_altitude_m)        
            
    time_start = time.time()
    start_position =np.array([drone.Latitude_deg,
                        drone.Longitude_deg,
                        drone.Absolute_altitude_m])
    try_count = 0

    time_now = time.time()
    goal = np.array([latitude_goal,
                    longitude_goal,
                    drone.Absolute_altitude_m])
    current = np.array([drone.Latitude_deg,
                        drone.Longitude_deg, 
                        drone.Absolute_altitude_m])
    dist = la.norm(goal - current)
    error = 0
    de = 0
    ie = 0
    # while True:

    while dist < 0.5:
        if time.time() - time_start > time_fin:
            logger_info.info("not found")
            await drone.Loop_goto_location(latitude_target=start_position[0],
                                            longitude_target=start_position[1],
                                            altitude_target=start_position[2])
            break
        time_pre = time_now
        error_pre = error
        time_now = time.time()
        T = time_now - time_pre
        error = goal - current #
        ##本来カメラを使う場合、以下を使用########################################################
        height = drone.Lidar
        yaw = drone.Yaw_deg
        await camera.take_pic()
        await camera.detect_center_cv()
        
        r = np.array([[camera.x*height*np.tan(alpha)],
                      [camera.y*height*np.tan(alpha)]]) #機体軸における、目標地点との差(ｍ)
        rotate = np.array([[np.cos(yaw), -np.sin(yaw)],
                           np.sin(yaw), np.cos(yaw)])
        r_e = np.dot(rotate,r).flatten() #地面固定座標系における、目標地点との差(ｍ)
        
        if la.norm(r_e) < 0.5: #十分近ければ50cm下降
            logger_info.info("down")
            if drone.Lidar < 1:
                break
            start_position =np.array([drone.Latitude_deg,
                                      drone.Longitude_deg,
                                      drone.Absolute_altitude_m])
            await drone.Loop_goto_location(latitude_target=drone.Latitude_deg,
                                           longitude_target=drone.Longitude_deg,
                                           altitude_target=drone.Absolute_altitude_m - 0.5)
            error = 0
            de = 0
            ie = 0
            continue
        elif camera.percent < 0.005:
            logger_info.info("try again")
            await drone.Loop_goto_location(latitude_target=start_position[0],
                                            longitude_target=start_position[1],
                                            altitude_target=start_position[2])
            await drone.Do_orbit(radius=try_count,
                                    velocity=0.1,
                                    yaw=0,
                                    latitude=start_position[0],
                                    longitude=start_position[1],
                                    altitude=start_position[2])
            try_count +=1
            continue
        #######################################################################################
        else :
            d_lat = r_e[0]/Cir_md*360 ##緯度差
            d_lon = r_e[1]/Cir_eq/np.cos(drone.Latitude_deg)*360 ##経度差
            error = np.array([d_lat,
                            d_lon,
                            0])        
            if not T == 0: 
                de = (error - error_pre)/T
                ie += (error + error_pre)*T/2
            control = KP*error + KI*ie + KD*de #PID制御による制御量を決定
              
                
            ##シミュレーション環境でのみ以下の評価をする##########################################    
            noise = random.uniform(-1,1) ###########シミュレーション環境ではノイズを意図的に入れる
            ###################################################################################    
                
            ##制御器
            target = control* (1 + noise) + current #実際はnoiseはなし
            await drone.Loop_goto_location(latitude_target=target[0],
                                            longitude_target=target[1],
                                            altitude_target=target[2])
                
            ##シミュレーション環境でのみ以下の評価をする#################################
            current = np.array([drone.Latitude_deg,
                                drone.Longitude_deg, 
                                drone.Absolute_altitude_m])
            dist = la.norm(goal - current)
            ##########################################################################
        
    await drone.Hold()
    await asyncio.sleep(1)
    await drone.Land()
    await asyncio.sleep(2)
    return


        
if __name__ == "__main__":
    drone = Bee()
    camera = Camera()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())



