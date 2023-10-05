from queenbee.camera3 import Camera
# from queenbee.logger_drone import logger_info
import asyncio

async def run():
    camera = Camera()
    camera.hlst = [0,360]
    camera.slst = [0,100]
    camera.vlst = [0,40]
    
    camera.hlst2 = [0,360]
    camera.slst2 = [0,100]
    camera.vlst2 = [0,40]
    
    camera.pic_path = ".\\log\\2023-09-11_logger\\006\\000.jpg"
    try:
        # while True:
        # await camera.take_pic()
        await camera.detect_center_cv()
        print(f"x{camera.x}")
        print(f"y{camera.y}")
        print(f"percent:{camera.percent}")
        await asyncio.sleep(2)
    finally:
        # camera.close()
        pass
    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    
    