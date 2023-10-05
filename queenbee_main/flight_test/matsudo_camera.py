#!/usr/bin/env python3
from queenbee.camera import Camera
import asyncio
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan
from queenbee.bee import Bee
from queenbee.logger_drone import logger_info, log_file_r
# from queenbee.plotter import df_lidar, plot_lidar, df_GPS, plot_GPS, plot_position, map_GPS
SYSTEMADDRESS = "serial:///dev/ttyACM0:115200"
altitude_hover=3

# latitude_start=35.7963106###松戸の橋の座標
# longitude_start=139.89165

# latitude_start = 35.715556
# longitude_start = 139.760441

async def use_camera():
    camera = Camera()
    try:
        while True:
            await camera.take_pic()
            await camera.detect_center_cv()
            logger_info.info(camera.center)
            await asyncio.sleep(2)
    finally:
        camera.close()


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
        drone.Loop_atitude()
    ]
    await asyncio.gather(*coroutines)

async def main_run():
    await asyncio.sleep(2)
    latitude_start = drone.Latitude_deg
    longitude_start = drone.Longitude_deg
    mission_items = []
    mission_items.append(MissionItem(latitude_start,
                                     longitude_start,
                                     altitude_hover,
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
        await asyncio.sleep(0.01)
        mission_finished = await drone.mission.is_mission_finished()
        if mission_finished:
            break        
    await drone.Land()
    await asyncio.sleep(10)

        
if __name__ == "__main__":
    drone = Bee()
    camera = Camera()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
