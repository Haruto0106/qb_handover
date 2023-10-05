from mavsdk import System
import mavsdk
import asyncio
import queenbee.logger
from queenbee.logger import logger_info, log_format


async def run():
    drone = System()
    await drone.connect(system_address="serial:///dev/ttyACM0:115200")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position estimate OK")
            break
    GPS_task = asyncio.ensure_future(print_GPS(drone))
    
    while True:
        await asyncio.sleep(2)


async def print_status_text(drone):
    try:
        async for status_text in drone.telemetry.status_text():
            print(f"Status: {status_text.type}: {status_text.text}")
    except asyncio.CancelledError:
        return


async def print_GPS(drone):
    async for position in drone.telemetry.position():        
        abs_altitude = position.absolute_altitude_m
        latitude = position.latitude_deg
        longitude = position.longitude_deg
        rel_altitude = position.relative_altitude_m
        lat=str(latitude)
        lon=str(longitude)
        abs_alt=str(abs_altitude)
        rel_alt=str(rel_altitude)
        print(f'RelAltitude:{rel_alt}\n')
        print(f'AbsAltitude:{abs_alt}\n')
        print(f'Latitude:{lat}\n')
        print(f'Longitude:{lon}\n')
        logger_info.info(log_format(relative_altitude = rel_alt,
                                    absolute_altitude= abs_alt,
                                    latitude= lat,
                                    longitude= lon))

        await asyncio.sleep(2)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())