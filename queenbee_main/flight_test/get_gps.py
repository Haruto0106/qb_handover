from queenbee.bee import Bee
import asyncio
SYSTEM_ADDRESS="serial:///dev/ttyACM0:115200"
async def main():
     await drone.Connect(system_address=SYSTEM_ADDRESS)
     await drone.Catch_GPS()
     main_coroutines = [ 
           drone.Loop_position(),
           drone.Loop_log()
      ]
     await asyncio.gather(*main_coroutines)


if __name__ == "__main__":
     drone = Bee()
     asyncio.run(main())