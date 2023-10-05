import asyncio
from mavsdk import System
import queenbee.logger
from queenbee.logger import logger_info, log_format
import threading
async def run():
    global drone
    drone = System()
    await drone.connect(system_address="serial:///dev/ttyACM0:115200")

    status_text_task = asyncio.ensure_future(print_status_text(drone))

    print("Waiting for drone to connect...")
    logger_info.info("Waiting for drone to connect...")
    
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            logger_info.info("-- Connected to drone!")
            break

    print("waiting for pixhawk to hold")
    logger_info.info("waiting for pixhawk to hold")
    flag = False
    while True:
       if flag==True:
           break
       async for flight_mode in drone.telemetry.flight_mode():
           if str(flight_mode) == "HOLD":
               print("-- Hold")
               logger_info.info("-- Hold")
               flag=True
               break
           else:
               try:
                   await drone.action.hold()
               except Exception as e:
                   print(e)
                   logger_info.error(e)
                   drone = System()
                   await drone.connect(system_address="serial:///dev/ttyACM0:115200")
                   print("Waiting for drone to connect...")
                   logger_info.info("Waiting for drone to connect...")
                   async for state in drone.core.connection_state():

                        if state.is_connected:
                            
                            print(f"-- Connected to drone!")
                            logger_info.info("-- Connected to drone!")
                            break
                   break 




    print("Waiting for drone to have a global position estimate...")
    logger_info.info("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position estimate OK")
            logger_info.info("-- Global position estimate OK")
            break
    GPS_task = asyncio.ensure_future(print_GPS(drone))
    distance_task = asyncio.ensure_future(print_distance(drone))

    


    
    print("-- Arming")
    logger_info.info("-- Arming")
    await drone.action.arm()
    print("-- Armed")
    logger_info.info("-- Armed")
    
    await asyncio.sleep(5)


    print("-- Taking off")
    logger_info.info("-- Taking off")
    await drone.action.takeoff()
    print("-- Taked off")
    
    print("Waiting 10 seconds")
    await asyncio.sleep(10)

    print("-- Landing")
    logger_info.info("-- Landing")
    await drone.action.land()
    print("-- Landed")
    logger_info.info("-- Landed")

    status_text_task.cancel()
    
    
    
async def print_status_text(drone):
    try:
        async for status_text in drone.telemetry.status_text():
            print(f"Status: {status_text.type}: {status_text.text}")
    except asyncio.CancelledError:
        return

async def print_distance(drone):
    async for distance_sensor in drone.telemetry.distance_sensor():
        # asyncio.sleep(2)
        try:
            distance = distance_sensor.current_distance_m
            # dist =str(distance)[0:9]
            dist =distance
            print(f"distance:{dist}\n")
            logger_info.info(log_format(distance=dist))
            await asyncio.sleep(2)
        except Exception as e:
            print(e)
            logger_info.error(e)
            return
        

async def print_GPS(drone):
    async for position in drone.telemetry.position():        
        abs_altitude = position.absolute_altitude_m
        latitude = position.latitude_deg
        longitude = position.longitude_deg
        rel_altitude = position.relative_altitude_m
        lat=str(latitude)[0:9]
        lon=str(longitude)[0:9]
        abs_alt=str(abs_altitude)[0:9]
        rel_alt=str(rel_altitude)[0:9]
        print(f'RelAltitude:{rel_alt}\n')
        print(f'AbsAltitude:{abs_alt}\n')
        print(f'Latitude:{lat}\n')
        print(f'Longitude:{lon}\n')
        logger_info.info(log_format(relative_altitude = rel_alt,
                                    absolute_altitude= abs_alt,
                                    latitude= lat,
                                    longitude= lon))
        await asyncio.sleep(2)
      
async def kill_drone():
    global drone
    input1 = input("killする場合は文字列を入力してください")
    if input1 != "continue":
        print("drone killed by you")
        logger_info.warning("-- Killing")
        await drone.action.kill()
        logger_info.warning("-- Killed")
        return

def main_func():
    asyncio.run(run())
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(run())

def kill_drone_func():
    asyncio.run(kill_drone())
    # loop2 = asyncio.get_event_loop()
    # loop2.run_until_complete(kill_drone())

thread1 = threading.Thread(target=main_func)
thread2 = threading.Thread(target=kill_drone_func)
thread1.start()
thread2.start()
thread1.join()
thread2.join()