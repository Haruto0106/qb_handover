#!/usr/bin/env python3

import asyncio
from mavsdk import System

async def run():
    drone = System()
    # await drone.connect(system_address="udp://:14540")
    await drone.connect(system_address="serial:///dev/ttyACM0:115200")
    status_text_task = asyncio.ensure_future(print_status_text(drone))
    
    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    print("waiting for pixhawk to hold")
    flag = False
    while True:
       if flag==True:
           break
       async for flight_mode in drone.telemetry.flight_mode():
           if str(flight_mode) == "HOLD":
               print("hold確認")
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
                   async for state in drone.core.connection_state():

                        if state.is_connected:
                            
                            print(f"-- Connected to drone!")
                            break
                   break 




    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position estimate OK")
            break
    
    print("-- Arming")
    await drone.action.arm()
    
    await asyncio.sleep(5)


    print("-- Taking off")
    await drone.action.takeoff()

    await asyncio.sleep(10)
    print("-- Landing")
    await drone.action.land()

    status_text_task.cancel()
    
    
    
async def print_status_text(drone):
    try:
        async for status_text in drone.telemetry.status_text():
            print(f"Status: {status_text.type}: {status_text.text}")
    except asyncio.CancelledError:
        return


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
