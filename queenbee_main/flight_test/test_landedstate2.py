#!/usr/bin/env python3

import asyncio
from mavsdk import System
from queenbee.bee_with_landedstate import Bee
from queenbee.with_landedstate_logger import logger_info, log_file_r
from queenbee.plotter import df_lidar, plot_lidar, df_GPS, plot_GPS, plot_position, map_GPS


async def run():
    # global drone
    # global dist,lat,lon,abs_alt,rel_alt
    # dist,lat,lon,abs_alt,rel_alt = 0,0,0,0,0
    # await drone.connect(system_address="udp://:14540")
    await drone.Connect(system_address="serial:///dev/ttyACM0:115200")
    #await drone.Catch_GPS()
    #await drone.Loop_hold_wait(system_address="serial:///dev/ttyACM0:115200")
    #await drone.Arm()
    

    coroutines = [
        #main_run(),
        drone.Get_flight_mode(),
        drone.Get_position(),
        drone.Get_lidar(),
        drone.Get_landed_State(),
        drone.Loop_log_with_landedstate(),
        drone.Loop_status_text(),
        # df_lidar(),
        # df_GPS(),
        # plot_lidar(),
        # plot_GPS(),
        # plot_position(),
        # map_GPS()
        
        # get_distance(),
        # loop_print()
        # get_GPS(),
        # loop_print_GPS()
    ]
    await asyncio.gather(*coroutines)

async def main_run():
    await asyncio.sleep(3)#8秒だと長すぎてarm解除された
    await drone.Takeoff()
    while drone.Lidar <= 0.5:#1.5mだとテント突き抜けそう、0.3mでもいいかも
        await asyncio.sleep(0.5)
    await drone.Hold()
    await asyncio.sleep(5)
    await drone.Land()  

if __name__ == "__main__":
    drone = Bee()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())