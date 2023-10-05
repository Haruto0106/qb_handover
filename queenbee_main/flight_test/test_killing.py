from mavsdk import System
import asyncio
import threading

TAKEOFF_ALTITUDE = 1.5

async def run():
    global drone
    drone = System()
    await drone.connect(system_address="serial:///dev/ttyACM0:115200")

    status_text_task = asyncio.ensure_future(print_status_text(drone))


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
    # print('gpsinfo is {}'.format(drone.telemetry.gps_info()))
    print_altitude_task = asyncio.ensure_future(print_altitude(drone))
    print_flight_mode_task = asyncio.ensure_future(print_flight_mode(drone))
    
    print('-- Hold')
    await drone.action.hold()
    
    print("-- Arming")
    await drone.action.arm()

    print("-- Taking off")
    await drone.action.set_takeoff_altitude(TAKEOFF_ALTITUDE)
    await drone.action.takeoff()

    await asyncio.sleep(10)

    print("-- Landing")
    await drone.action.land()


async def print_status_text(drone):
    try:
        async for status_text in drone.telemetry.status_text():
            print(f"Status: {status_text.type}: {status_text.text}")
    except asyncio.CancelledError:
        return

        
async def print_altitude(drone):
    """ Prints the altitude when it changes """

    previous_altitude = 0.0

    async for position in drone.telemetry.position():
        altitude_now = position.relative_altitude_m
        if abs(previous_altitude - altitude_now) >= 0.1:
            previous_altitude = altitude_now
            print(f"Altitude: {altitude_now}")

        if altitude_now > 1.2:
            print("--Landing -- <print_altitude> detected altitude_now > 1.2")
            await drone.action.land()


async def print_flight_mode(drone):
    """ Prints the flight mode when it changes """

    previous_flight_mode = None

    async for flight_mode in drone.telemetry.flight_mode():
        if flight_mode != previous_flight_mode:
            previous_flight_mode = flight_mode
            print(f"Flight mode: {flight_mode}")

async def kill_drone():
    global drone
    input1 = input("killする場合は文字列を入力してください")
    if input1 != "continue":
        await drone.action.kill()
        print("drone killed by you")

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