#!/usr/bin/env python3

import asyncio
from mavsdk import System
from queenbee.bee import Bee
from queenbee.logger_drone import logger_info, log_file_r
from queenbee.plotter import df_lidar, plot_lidar, df_GPS, plot_GPS, plot_position, map_GPS


async def run():
    # global drone
    # global dist,lat,lon,abs_alt,rel_alt
    # dist,lat,lon,abs_alt,rel_alt = 0,0,0,0,0
    # await drone.connect(system_address="udp://:14540")
    await drone.Connect(system_address="serial:///dev/ttyACM0:115200")
    await drone.Catch_GPS()
    await drone.Loop_hold_wait(system_address="serial:///dev/ttyACM0:115200")
    await drone.Arm()
    

    coroutines = [
        main_run(),
        drone.Loop_flight_mode(),
        drone.Loop_position(),
        drone.Loop_lidar(),
        drone.Loop_log(),
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
    while drone.Lidar <= 0.3:#1.5mだとテント突き抜けそう、0.3mでもいいかも
        await asyncio.sleep(0.05)
    #await drone.Hold()
    #await asyncio.sleep(5)
    await drone.Land()  

if __name__ == "__main__":
    drone = Bee()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())