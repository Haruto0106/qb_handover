from queenbee.camera2 import Camera
from queenbee.logger_drone import logger_info
import asyncio
from omegaconf import OmegaConf
import sys
lst = ["matsudo", "arliss"]

async def run():
    try:
        condition = sys.argv[1]
    except IndexError as e:
        logger_info.error(e)
        logger_info.info("条件未入力")
        exit()
        
    if condition in lst:
        if condition == "matsudo":
            with open("./config/matsudo_config.yaml", mode="r") as f:
                conf = OmegaConf.load(f)
        elif condition == "arliss" :
            with open("./config/arliss_config.yaml", mode="r") as f:
                conf = OmegaConf.load(f)
    else :
        logger_info.warning("--condition not specified")
        exit()
    camera = Camera()
    camera.hlst = conf.hsv.h
    camera.slst = conf.hsv.s
    camera.vlst = conf.hsv.v
    camera.hlst2 = conf.hsv2.h
    camera.slst2 = conf.hsv2.s
    camera.vlst2 = conf.hsv2.v
    # camera.shutter_speed = conf.photo.shutter_speed
    # camera.framerate = conf.photo.framerate
    # camera.exposure_mode = conf.photo.exposure_mode
    
    try:
        # while True:
        await camera.take_pic()
        await camera.detect_center_cv()
        logger_info.info(f"x{camera.x}")
        logger_info.info(f"y{camera.y}")
        logger_info.info(f"percent:{camera.percent}")
        await asyncio.sleep(2)
    finally:
        camera.close()
    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    
    