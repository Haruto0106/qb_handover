#!/usr/bin/env python3

import asyncio
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan
from queenbee.bee import Bee
from queenbee.logger_drone import logger_info, log_file_r
from queenbee.plotter import df_lidar, plot_lidar, df_GPS, plot_GPS, plot_position, map_GPS
SYSTEMADDRESS = "serial:///dev/ttyACM0:115200"
altitude_hover=3
altitude_goto = 3
# latitude_start=35.7963106###松戸の橋の座標
# longitude_start=139.89165

# latitude_start=35.796174###松戸の橋近くの座標
# longitude_start=139.891552

# latitude_goal = 35.796021
# longitude_goal = 139.891437


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
        drone.Loop_mission_progress()
    ]
    await asyncio.gather(*coroutines)

async def main_run():
    await asyncio.sleep(2)
    await drone.Arm()
    latitude_start = drone.Latitude_deg
    longitude_start = drone.Longitude_deg
    altitude_home = drone.Absolute_altitude_m
    altitude_goal = altitude_home + altitude_goto
    await drone.Loop_goto_location(altitude_target=altitude_goal,
                                   longitude_target=longitude_start,
                                   latitude_target=latitude_start)
    await drone.Hold()
    await asyncio.sleep(2)
    await drone.Land()
    await asyncio.sleep(2)
    return

        
if __name__ == "__main__":
    drone = Bee()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
