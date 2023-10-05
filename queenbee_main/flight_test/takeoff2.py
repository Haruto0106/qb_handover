#!/usr/bin/env python3

import asyncio
from mavsdk import System
from queenbee.bee import Bee
from queenbee.logger import logger_info, log_file_r
from queenbee.plotter import df_lidar, plot_lidar, df_GPS, plot_GPS, plot_position, map_GPS
SYSTEMADDRESS = "serial:///dev/ttyACM0:115200"

async def run():
    await drone.Connect(SYSTEMADDRESS)
    await drone.Catch_GPS()
    await drone.Loop_hold_wait(SYSTEMADDRESS)
    await drone.Arm()

    coroutines = [
        main_run(),
        drone.Get_flight_mode(),
        drone.Get_position(),
        drone.Get_lidar(),
        drone.Loop_log(),
        drone.Loop_status_text(),
        df_lidar(),
        df_GPS(),
        # plot_lidar(),
        # plot_GPS(),
        plot_position(),
        map_GPS()        
    ]
    await asyncio.gather(*coroutines)

async def main_run():
    await asyncio.sleep(2)
    await drone.Takeoff()
    await asyncio.sleep(10)
    # await drone.Land()
    await drone.task_land()
    
    
        
if __name__ == "__main__":
    drone = Bee()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
