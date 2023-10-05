import time                         #時間制御用のモジュールをインポート
import asyncio
import threading
import pandas as pd
from datetime import datetime, timedelta
from omegaconf import OmegaConf
import sys
from queenbee.bee import Bee, image_process
from queenbee.logger_drone import logger_info

# from queenbee.plotter import df_lidar, plot_lidar, df_GPS, plot_GPS, plot_position, map_GPS
# from queenbee.camera import Camera
from queenbee.lora_queenbee import Lora

SYSTEM_ADDRESS="serial:///dev/ttyACM0:115200"
lst = ["matsudo", "nse", "arliss"]
condition = ""


async def main_flight():###Drone飛行の行程の関数
    await asyncio.sleep(3)
    await drone.Arm()
    latitude_home = drone.Latitude_deg
    longitude_home = drone.Longitude_deg
    altitude_home = drone.Absolute_altitude_m
    
    await drone.Set_takeoff_altitude(5)
    await drone.Takeoff()
    while drone.Lidar < 3:
        await asyncio.sleep(0.05)
    #中継位置１
    await drone.Loop_goto_location(latitude_target=lat_target1,
                                   longitude_target=lon_target1,
                                   altitude_target=alt_target1)
    await drone.Hold()    
    await drone.Land()  

async def main_drone():###Droneの全て,LoRaも
    await drone.Connect(system_address=SYSTEM_ADDRESS)
    await drone.Catch_GPS()
    await drone.Loop_hold_wait(system_address=SYSTEM_ADDRESS)
    await lora.power_on()
    coroutines = [
        main_flight(),
        drone.Loop_flight_mode(),
        lora.cycle_send_position(drone),
        drone.Loop_position(),
        drone.Loop_lidar(),
        drone.Loop_log(),
        drone.Loop_status_text(),
        drone.Loop_atitude()
        # map_GPS()
    ]
    await asyncio.gather(*coroutines)



####################################################################################
if __name__ == '__main__':#同時に処理を実行する
    drone = Bee()
    # camera = Camera()
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
    loop.run_until_complete(main_drone())###Droneここまで