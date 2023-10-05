from queenbee.lora_queenbee import Lora
from queenbee.bee import Bee
import asyncio
import threading
SYSTEM_ADDRESS="serial:///dev/ttyACM0:115200"
async def main():
    await lora.power_on()
    
if __name__ == "__main__":
    lora = Lora()
    drone = Bee()
    asyncio.run(main())
    thread1 = threading.Thread(target = asyncio.run(lora.do_cycle_send_progress_test()))
    thread1.start()
    thread1.join()     

