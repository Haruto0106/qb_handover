#!/usr/bin/env python3

import asyncio
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan
from queenbee.bee import Bee
from queenbee.logger_drone import logger_info, log_file_r
# from queenbee.plotter import df_lidar, plot_lidar, df_GPS, plot_GPS, plot_position, map_GPS
SYSTEMADDRESS = "serial:///dev/ttyACM0:115200"

# latitude_start=35.7963106###松戸の橋の座標
# longitude_start=139.89165

# latitude_start = 35.715556
# longitude_start = 139.760441

# latitude_goal = 35.796723   #ゲートボール場の座標 
# longitude_goal = 139.8918259

# latitude_goal = 35.7926509   #畑横の座標
# longitude_goal = 139.8908180

async def run():
    await drone.Connect(system_address=SYSTEMADDRESS)
    # await drone.Catch_GPS()]
    # await drone.Arm()
        
    coroutines = [
        main_run(),
        drone.Loop_flight_mode(),
        # drone.Loop_position(),
        drone.Loop_lidar(),
        drone.Loop_mission_progress(),
        # drone.Loop_log(),
        drone.Loop_pressure(),
        drone.Loop_atitude(),
        # drone.Loop_temperature(),
        drone.Loop_odometry(),
        drone.Loop_acceleration_frd(),
        drone.Loop_status_text()
    ]
    await asyncio.gather(*coroutines)

async def main_run():
    while True:
        # logger_info.info(f"pressure: {drone.Pressure}")
        logger_info.info(f"yaw: {drone.Yaw_deg}")
        # logger_info.info(f"temp: {drone.Temperature}")
        logger_info.info(f"X: {drone.X_m}, Y:{drone.Y_m}, Z:{drone.Z_m}")
        # logger_info.info(f"Vx: {drone.X_m_s}, Vy:{drone.Y_m_s}, Vz:{drone.Z_m_s}")
        # logger_info.info(f"roll: {drone.Odometry_roll_rad_s}, pitch:{drone.Odometry_pitch_rad_s}, yaw:{drone.Odometry_yaw_rad_s}")
        # logger_info.info(f"a_x:{drone.a_x}, a_y:{drone.a_y}, a_z:{drone.a_z}")
        await asyncio.sleep(1)
        
if __name__ == "__main__":
    drone = Bee()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
