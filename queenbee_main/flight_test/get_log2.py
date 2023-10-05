#!/usr/bin/env python3

import asyncio
from mavsdk import System
from queenbee.bee import Bee
from queenbee.logger import logger_info, log_file_r
from queenbee.plotter import df_lidar, plot_lidar, df_GPS, plot_GPS, plot_position, map_GPS


async def run():
    # global drone
    drone = Bee()
    # global dist,lat,lon,abs_alt,rel_alt
    # dist,lat,lon,abs_alt,rel_alt = 0,0,0,0,0
    # await drone.connect(system_address="udp://:14540")
    await drone.Connect(system_address="serial:///dev/ttyACM0:115200")
    #await drone.Catch_GPS()

    coroutines = [
        drone.Get_flight_mode(),
        #drone.Get_position(),
        drone.Get_lidar(),
        drone.Loop_log(),
        drone.Loop_status_text(),
        df_lidar(),
        #df_GPS(),
        plot_lidar(),
        # plot_GPS(),
        #plot_position(),
        #map_GPS()
        
        # get_distance(),
        # loop_print()
        # get_GPS(),
        # loop_print_GPS()
    ]
    await asyncio.gather(*coroutines)

        
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
