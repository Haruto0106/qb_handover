#!/usr/bin/env python3

import asyncio
from mavsdk import System
import threading

async def run():
    global drone
    global dist
    drone = System()
    # await drone.connect(system_address="udp://:14540")
    await drone.connect(system_address="serial:///dev/ttyACM0:115200")
    status_text_task = asyncio.ensure_future(print_status_text(drone))
    
    distance_task = asyncio.ensure_future(get_distance())
    # print_task = asyncio.ensure_future(print_distance())
    
    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break
        
    # await get_distance()
    while True:
        await asyncio.sleep(2)
        print("loop")
        print(f"distance:{dist}")


    status_text_task.cancel()
    
    
    
async def print_status_text(drone):
    try:
        async for status_text in drone.telemetry.status_text():
            print(f"Status: {status_text.type}: {status_text.text}")
    except asyncio.CancelledError:
        return
async def get_distance():
    global drone
    global dist
    global count
    count = 0
    # await drone.telemetry.distance_sensor()
    async for distance_sensor in drone.telemetry.distance_sensor():
        distance = distance_sensor.current_distance_m
        dist=float(distance)
        # print(dist)
        # print(count)
        # count += 1
        # print(f"distance: {dist}")

# async def print_distance():
#     await asyncio.sleep(0.1)
#     global dist
#     print(dist)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())

