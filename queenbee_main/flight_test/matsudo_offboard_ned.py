#!/usr/bin/env python3


import asyncio

from mavsdk import System
from mavsdk.offboard import (OffboardError, PositionNedYaw)
from queenbee.bee import Bee
from queenbee.logger_drone import logger_info, log_file_r
# from queenbee.plotter import df_lidar, plot_lidar, df_GPS, plot_GPS, plot_position, map_GPS


async def run():  
    await drone.Connect(system_address="serial:///dev/ttyACM0:115200")
    await drone.Catch_GPS()
    await drone.Loop_hold_wait(system_address="serial:///dev/ttyACM0:115200")
    

    coroutines = [
        main_run(),
        drone.Loop_flight_mode(),
        drone.Loop_position(),
        drone.Loop_lidar(),
        drone.Loop_log(),
        drone.Loop_status_text()
    ]
    await asyncio.gather(*coroutines)


async def main_run():
    await asyncio.sleep(2)
    await drone.Arm()
    await drone.Set_takeoff_altitude(5)
    await drone.Takeoff()
    while drone.Lidar <= 3:
        await asyncio.sleep(0.05)
    logger_info.info("hold")
    await drone.Hold()
    await asyncio.sleep(5)    
    
    logger_info.info("-- Setting initial setpoint")
    await drone.offboard.set_position_ned(
        PositionNedYaw(0.0, 0.0, 0.0, 0.0))
    await asyncio.sleep(3)
    
    logger_info.info("-- Starting offboard")
    while True:
        try:
            await drone.offboard.start()
            break
        except OffboardError as error:
            logger_info.error(f"Starting offboard mode failed with error code: \
                {error._result.result}")
            continue


    logger_info.info("-- Go 0m North, 0m East, -5m Down")
    await drone.offboard.set_position_ned(
        PositionNedYaw(0.0, 0.0, -5, 0.0))
    await asyncio.sleep(10)

    logger_info.info("-- Go 2m North, 0m East, 0m Down")
    await drone.offboard.set_position_ned(
        PositionNedYaw(2, 0.0, 0.0, 0.0))
    await asyncio.sleep(10)

    logger_info.info("-- Wait for a bit")
    await drone.offboard.set_position_ned(
        PositionNedYaw(0.0, 0.0, 0.0, 0.0))
    await asyncio.sleep(2)

    logger_info.info("-- Go 0m North, 2m East, 0m Down")
    await drone.offboard.set_position_ned(
        PositionNedYaw(0.0, 2, 0.0, 0.0))
    await asyncio.sleep(10)

    logger_info.info("-- Wait for a bit")
    await drone.offboard.set_position_ned(
        PositionNedYaw(0.0, 0.0, 0.0, 0.0))
    await asyncio.sleep(2)
    
    logger_info.info("-- Go -2m North, -2m East, 0m Down")
    await drone.offboard.set_position_ned(
        PositionNedYaw(-2, -2, 0.0, 0.0))
    await asyncio.sleep(10)

    logger_info.info("-- Wait for a bit")
    await drone.offboard.set_position_ned(
        PositionNedYaw(0.0, 0.0, 0.0, 0.0))
    await asyncio.sleep(2)
    
    logger_info.info("-- turn")
    await drone.offboard.set_position_ned(
        PositionNedYaw(0.0, 0.0, 0.0, 180))
    await asyncio.sleep(10)
        
    logger_info.info("-- Stopping offboard")
    while True:
        try:
            await drone.offboard.stop()
            break
        except OffboardError as error:
            logger_info.error(f"Stopping offboard mode failed with error code: \
                {error._result.result}")
            continue
    
    await drone.Hold()
    await drone.Land()


if __name__ == "__main__":
    drone = Bee()
    # Run the asyncio loop
    asyncio.run(run())