from queenbee.lora_queenbee import Lora
from queenbee.class_case import Case
import asyncio
import time
async def main():
     lora = Lora()
     case_ = Case()
     await lora.power_on()
     lora.send()###humnaviにはなぜかなかった
      #      lora.cycle_receive_lora(drone)
     case_.nichrome_on(case_.nichrome_stand, case_.nichrome_time)#これでケースのテグスを切るためのニクロム線が動作。テグス切れる
     time.sleep(10)
     case_.nichrome_on(case_.nichrome_arm, case_.nichrome_time)

     lora.send()


if __name__ == "__main__":
      asyncio.run(main())
    