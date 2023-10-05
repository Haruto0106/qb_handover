from queenbee.camera import Camera
from queenbee.logger_drone import logger_info
import asyncio

async def run():
    camera = Camera()
    while True:
        try:
            await camera.take_pic()
            await camera.detect_center_cv()
            logger_info.info(camera.center)
            await asyncio.sleep(2)
        except KeyboardInterrupt:
            camera.close()
    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    
    