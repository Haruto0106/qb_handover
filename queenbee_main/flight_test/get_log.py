#!/usr/bin/env python3

import asyncio
from mavsdk import System
from queenbee.bee import Bee
from queenbee.logger import logger_info


async def run():
    global drone
    global dist,lat,lon,abs_alt,rel_alt
    drone = Bee()
    dist,lat,lon,abs_alt,rel_alt = 0,0,0,0,0
    # await drone.connect(system_address="udp://:14540")
    await drone.Connect(system_address="serial:///dev/ttyACM0:115200")
    await drone.Catch_GPS()

    coroutines = [
        drone.Get_flight_mode(),
        drone.Get_position(),
        drone.Get_lidar(),
        drone.Loop_log(),
        drone.Loop_status_text()
        # get_distance(),
        # loop_print()
        # get_GPS(),
        # loop_print_GPS()
    ]
    await asyncio.gather(*coroutines)

async def get_distance():
    global drone
    global dist
    async for distance_sensor in drone.telemetry.distance_sensor():
        distance = distance_sensor.current_distance_m
        dist=float(distance)


async def get_GPS():
    global drone
    global lat,lon,abs_alt,rel_alt
    async for position in drone.telemetry.position():        
        abs_altitude = position.absolute_altitude_m
        latitude = position.latitude_deg
        longitude = position.longitude_deg
        rel_altitude = position.relative_altitude_m
        lat=str(latitude)[0:9]
        lon=str(longitude)[0:9]
        abs_alt=str(abs_altitude)[0:9]
        rel_alt=str(rel_altitude)[0:9]


async def loop_print_distance():
    while True:
        global dist
        print(f"distance:{dist}")
        await asyncio.sleep(2)


async def loop_print_GPS():
    while True:
        global lat,lon,abs_alt,rel_alt
        print(f'RelAltitude:{rel_alt}\n')
        print(f'AbsAltitude:{abs_alt}\n')
        print(f'Latitude:{lat}\n')
        print(f'Longitude:{lon}\n')
        await asyncio.sleep(2)

        
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
