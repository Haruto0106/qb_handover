#!/usr/bin/env python3

import asyncio
from mavsdk import System
import queenbee.logger
from queenbee.logger import logger_info, log_format

async def run():
    drone = System()
    # await drone.connect(system_address="udp://:14540")
    await drone.connect(system_address="serial:///dev/ttyACM0:115200")
    status_text_task = asyncio.ensure_future(print_status_text(drone))
    
    print("Waiting for drone to connect...")
    logger_info.info("Waiting for drone to connect...")
    
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            logger_info.info("-- Connected to drone!")
            break

    print("waiting for pixhawk to hold")
    logger_info.info("waiting for pixhawk to hold")
    flag = False
    while True:
       if flag==True:
           break
       async for flight_mode in drone.telemetry.flight_mode():
           if str(flight_mode) == "HOLD":
               print("hold確認")
               logger_info.info("hold確認")
               flag=True
               break
           else:
               try:
                   await drone.action.hold()
               except Exception as e:
                   print(e)
                   drone = System()
                   await drone.connect(system_address="serial:///dev/ttyACM0:115200")
                   print("Waiting for drone to connect...")
                   logger_info.info("Waiting for drone to connect...")
                   async for state in drone.core.connection_state():

                        if state.is_connected:
                            
                            print(f"-- Connected to drone!")
                            logger_info.info("-- Connected to drone!")
                            break
                   break 




    print("Waiting for drone to have a global position estimate...")
    logger_info.info("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position estimate OK")
            logger_info.info("-- Global position estimate OK")
            break
    GPS_task = asyncio.ensure_future(print_GPS(drone))

    


    
    print("-- Arming")
    logger_info.info("-- Arming")
    await drone.action.arm()
    print("-- Armed")
    logger_info.info("-- Armed")
    
    await asyncio.sleep(5)


    print("-- Taking off")
    logger_info.info("-- Taking off")
    await drone.action.takeoff()
    print("-- Taked off")
    
    print("Waiting 10 seconds")
    await asyncio.sleep(10)
    
    print("-- Landing")
    logger_info.info("-- Landing")
    await drone.action.land()
    print("-- Landed")
    logger_info.info("-- Landed")

    status_text_task.cancel()
    
    
    
async def print_status_text(drone):
    try:
        async for status_text in drone.telemetry.status_text():
            print(f"Status: {status_text.type}: {status_text.text}")
    except asyncio.CancelledError:
        return



async def print_GPS(drone):
    async for position in drone.telemetry.position():        
        abs_altitude = position.absolute_altitude_m
        latitude = position.latitude_deg
        longitude = position.longitude_deg
        rel_altitude = position.relative_altitude_m
        lat=str(latitude)[0:9]
        lon=str(longitude)[0:9]
        abs_alt=str(abs_altitude)[0:9]
        rel_alt=str(rel_altitude)[0:9]
        print(f'RelAltitude:{rel_alt}\n')
        print(f'AbsAltitude:{abs_alt}\n')
        print(f'Latitude:{lat}\n')
        print(f'Longitude:{lon}\n')
        logger_info.info(log_format(relative_altitude = rel_alt,
                                    absolute_altitude= abs_alt,
                                    latitude= lat,
                                    longitude= lon))
        await asyncio.sleep(2)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
