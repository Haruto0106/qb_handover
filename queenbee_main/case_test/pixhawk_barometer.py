from mavsdk import System
import asyncio
from queenbee.bee import Bee

async def run():
    global pressure

    print("waiting for drone connect")
    await drone.connect(system_address="serial:///dev/ttyACM0:115200")
    print("drone connected")
    # coroutines = [
    #     Get_pressure(),
    #     print_pressure()
    # ]
    # asyncio.gather(*coroutines)
    
    
    coroutines = [
        drone.Get_pressure(),
        drone.Loop_pressure()
    ]
    await asyncio.gather(*coroutines)

async def Get_pressure():
    global pressure
    async for Pressure in drone.telemetry.scaled_pressure():
        pressure = Pressure.absolute_pressure_hpa

    
async def print_pressure():
    global pressure
    while True:
        try:
            print(f"pressure:{pressure}")
            asyncio.sleep(1)
        except Exception as e:
            print(e)
            asyncio.sleep(1)
            continue

if __name__ == '__main__':
    drone = Bee()
    asyncio.run(run())