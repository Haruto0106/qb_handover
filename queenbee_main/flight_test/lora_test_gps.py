from queenbee.lora_queenbee import Lora
from queenbee.bee import Bee
import asyncio
SYSTEM_ADDRESS="serial:///dev/ttyACM0:115200"
async def main():
     await lora.power_on()
     await drone.Connect(system_address=SYSTEM_ADDRESS)
     await drone.Catch_GPS()
     main_coroutines = [ 
           lora.cycle_send_position(drone),###humnaviにはなぜかなかった
           drone.Loop_position()
        #    lora.cycle_receive_lora(drone)
        #   lora.cycle_send()
      ]
     await asyncio.gather(*main_coroutines)


if __name__ == "__main__":
     lora = Lora()
     drone = Bee()
     asyncio.run(main())