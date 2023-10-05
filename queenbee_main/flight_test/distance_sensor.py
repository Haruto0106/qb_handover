#!/usr/bin/env python3

import asyncio
from mavsdk import System
import threading
from logging import NullHandler

async def run():
    global drone
    global dist
    dist = 0
    drone = System()
    # await drone.connect(system_address="udp://:14540")
    await drone.connect(system_address="serial:///dev/ttyACM0:115200")
    status_text_task = asyncio.ensure_future(print_status_text(drone))
    
    # distance_task = asyncio.ensure_future(get_distance())
    
    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break
    coroutines = [
        get_distance(),
        loop_print()
    ]
    await asyncio.gather(*coroutines)
    


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
    async for distance_sensor in drone.telemetry.distance_sensor():
        distance = distance_sensor.current_distance_m
        dist=float(distance)

async def loop_print():
    while True:
        global dist
        print(dist)
        await asyncio.sleep(2)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
