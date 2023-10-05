from queenbee.lora_queenbee import Lora
from queenbee.bee import Bee
import asyncio
SYSTEM_ADDRESS="serial:///dev/ttyACM0:115200"
async def main():
     await lora.power_on()
     main_coroutines = [ 
           lora.cycle_send2()
        #    lora.cycle_receive_lora(drone)
        #   lora.cycle_send()
      ]
     await asyncio.gather(*main_coroutines)


if __name__ == "__main__":
     lora = Lora()
     drone = Bee()
     asyncio.run(main())