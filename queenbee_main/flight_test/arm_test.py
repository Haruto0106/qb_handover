#!/usr/bin/env python3

import asyncio
from mavsdk import System
from queenbee.bee import Bee
from queenbee.logger_drone import logger_info, log_file_r
# from queenbee.plotter import df_lidar, plot_lidar, df_GPS, plot_GPS, plot_position, map_GPS


async def run():
    # global drone
    # global dist,lat,lon,abs_alt,rel_alt
    # dist,lat,lon,abs_alt,rel_alt = 0,0,0,0,0
    # await drone.connect(system_address="udp://:14540")

    await drone.Connect(system_address="serial:///dev/ttyACM0:115200", system_address_1= "serial:///dev/ttyACM1:115200")
    # await drone.Catch_GPS()
    # await drone.Loop_hold_wait()
    await drone.Loop_arm_wait()
    

    # coroutines = [
    #     main_run(),
    #     drone.Get_flight_mode(),
    #     drone.Get_position(),
    #     drone.Get_lidar(),
    #     drone.Loop_log(),
    #     drone.Loop_status_text(),
    #     df_lidar(),
    #     df_GPS(),
    #     # plot_lidar(),
    #     # plot_GPS(),
    #     plot_position(),
    #     map_GPS()
        
    #     # get_distance(),
    #     # loop_print()
    #     # get_GPS(),
    #     # loop_print_GPS()
    # ]
    # await asyncio.gather(*coroutines)

async def main_run():
    await asyncio.sleep(3)
    await drone.Takeoff()
    while drone.Lidar <= 1.5:
        await asyncio.sleep(0.5)
    await drone.Hold()
    await asyncio.sleep(5)
    await drone.Land()  

if __name__ == "__main__":
    drone = Bee()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())