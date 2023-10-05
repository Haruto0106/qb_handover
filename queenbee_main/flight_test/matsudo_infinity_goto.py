#!/usr/bin/env python3
from queenbee.lora_queenbee import Lora
import asyncio
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan
from queenbee.bee import Bee
from queenbee.logger_drone import logger_info, log_file_r
# from queenbee.plotter import df_lidar, plot_lidar, df_GPS, plot_GPS, plot_position, map_GPS
from omegaconf import OmegaConf
import sys
SYSTEMADDRESS = "serial:///dev/ttyACM0:115200"
altitude_hover=4

lst = ["matsudo", "nse", "arliss"]
condition = ""
# latitude_start=35.7963106###松戸の橋の座標
# longitude_start=139.89165

# latitude_start=35.796174###松戸の橋近くの座標
# longitude_start=139.891552

# latitude_goal = 35.796723   #ゲートボール場の座標 
# longitude_goal = 139.8918259

# latitude_goal = 35.7926509   #畑横の座標
# longitude_goal = 139.8908180

# latitude_goal = 35.7972205 # ゲートボール真ん中
# longitude_goal = 139.8921568

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
        lora.cycle_send_position(drone)
    ]
    await asyncio.gather(*coroutines)

async def main_run():
    counter = 0
    await asyncio.sleep(2)
    await drone.Arm()
    latitude_start = drone.Latitude_deg
    longitude_start = drone.Longitude_deg
    altitude_home = drone.Absolute_altitude_m
    await drone.Set_takeoff_altitude(5)
    await drone.Takeoff()
    while drone.Lidar < 4:
        await asyncio.sleep(0.05)
    altitude_goal = altitude_home + altitude_hover
    while True:
        await drone.Loop_goto_location(altitude_target=altitude_goal,
                                       latitude_target=latitude_start,
                                       longitude_target=longitude_start)
        counter += 1#片道の回数
        logger_info.info("The number of one-way trip:" + str(counter))
        await drone.Loop_goto_location(altitude_target=altitude_goal,
                                       latitude_target=lat_target1,
                                       longitude_target=lon_target1)    
        counter = counter + 1#片道の回数
        logger_info.info("The number of one-way trip:" + str(counter))
        if drone.Lidar > 10:#高すぎたら降ろす
            await drone.Land()
            break
    await asyncio.sleep(5)
    await drone.Land()

    return

        
if __name__ == "__main__":
    drone = Bee()
    lora = Lora()
    try:
        condition = sys.argv[1]
    except IndexError as e:
        logger_info.error(e)
        
    if condition in lst:
        if condition == "matsudo":
            with open("./config/matsudo_config.yaml", mode="r") as f:
                conf = OmegaConf.load(f)
        elif condition == "nse" :
            with open("./config/nse_config.yaml", mode="r") as f:
                conf = OmegaConf.load(f)
        elif condition == "arliss" :
            with open("./config/arliss_config.yaml", mode="r") as f:
                conf = OmegaConf.load(f)
        SYSTEM_ADDRESS = conf.system_address
        lat_target1 = conf.target1.latitude
        lon_target1 = conf.target1.longitude
        alt_target1 = conf.target1.altitude
    else :
        logger_info.warning("--condition not specified")
        ###初期化がうまくいかず、強制終了したことを、ハードで見て分かるような処理を入れたい(Lチカとか)
        exit()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
