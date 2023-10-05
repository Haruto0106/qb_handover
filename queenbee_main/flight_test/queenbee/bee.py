import asyncio
import datetime
import mavsdk
from mavsdk.mission import MissionItem,MissionPlan
import numpy as np
from mavsdk import server_utility
from queenbee.logger_drone import logger_info, log_format
from mavsdk.offboard import OffboardError, VelocityBodyYawspeed
import time
from camera import Camera

class Bee(mavsdk.System):
    def __init__(self):
        super().__init__()
        logger_info.info("Pixhawk initialized")
        # global position
        self.Latitude_deg = 0.0
        self.Longitude_deg = 0.0
        self.Absolute_altitude_m = 0.0
        self.Relative_altitude_m = 0.0
        # angle
        self.Pitch_deg = 0.0
        self.Roll_deg = 0.0
        self.Yaw_deg = 0.0
        # lidar
        self.Lidar = -1
        # flight mode
        self.Flight_mode = 0.0
        # gps
        self.num_satellites = 0.0
        self.fix_type = 0.0
        
        # landed state
        self.Landed_state = 0.0        
        # status_text
        self.Status_text = ""
        # mission progress
        self.Mission_progress = ""
        # pressure
        self.Pressure = 0.0
        # temperature
        self.Temperature = 0.0
        
        # offboard unit
        self.v_x = 0.0
        self.v_y = 0.0
        self.v_z = 0.0
        self.R = 0.0
        
        # acceleration
        self.a_x = 0.0
        self.a_y = 0.0
        self.a_z = 0.0
        
        # odometry
        self.X_m = 0.0
        self.Y_m = 0.0
        self.Z_m = 0.0
        self.X_m_s = 0.0
        self.Y_m_s = 0.0
        self.Z_m_s = 0.0
        self.Odometry_roll_rad_s = 0.0
        self.Odometry_pitch_rad_s = 0.0
        self.Odometry_yaw_rad_s = 0.0

###setup######################################################################################
    async def Connect(self, system_address= "serial:///dev/ttyACM0:115200", 
                      system_address_1 = "serial:///dev/ttyACM1:115200") -> None:
        # flag = False
        # while True:
        #     if flag==True:
        #         break
        #     logger_info.info(f"Waiting for drone to connect {system_address_1}")
        #     await self.connect(system_address=system_address_1)
        #     print("b")
        #     async for state in self.core.connection_state():
        #         print(state.is_connected)
        #         print("a")
        #         if state.is_connected:
        #             logger_info.info(f"-- connected Drone to {system_address}")
        #             flag=True
        #             break
        #         else:
        #             logger_info.info(f"Waiting for drone to connect {system_address}")                    
        #             await self.connect(system_address=system_address)
                     
        logger_info.info("Waiting for drone to connect...")
        await self.connect(system_address=system_address)

        async for state in self.core.connection_state():
            if state.is_connected:
                logger_info.info("Connected Drone!")
                break
            
            
    async def Catch_GPS(self):
            logger_info.info("Waiting for drone to have a global position estimate...")
            async for health in self.telemetry.health():
                if health.is_global_position_ok and health.is_home_position_ok:
                    logger_info.info("-- Global position estimate OK")
                    break

###getinfo#####################################################################################
    async def Get_lidar(self) -> None:
        async for distance_sensor in self.telemetry.distance_sensor():
            self.Lidar = (
                distance_sensor.current_distance_m
                * np.cos(np.deg2rad(self.Pitch_deg))
                * np.cos(np.deg2rad(self.Roll_deg))
            )

    async def Get_position(self) -> None:
        async for position in self.telemetry.position():
            self.Latitude_deg = position.latitude_deg
            self.Longitude_deg = position.longitude_deg
            self.Absolute_altitude_m = position.absolute_altitude_m
            self.Relative_altitude_m = position.relative_altitude_m
            
    async def Get_gps_info(self) -> None:
        """get number of satellites and fix type"""
        async for gps_info in self.telemetry.gps_info():
            self.num_satellites = gps_info.num_satellites
            self.fix_type = gps_info.fix_type

    async def Get_attitude_angle(self) -> None:
        """get angle from sensors"""
        async for angle in self.telemetry.attitude_euler():
            self.Pitch_deg = angle.pitch_deg
            self.Roll_deg = angle.roll_deg
            self.Yaw_deg = angle.yaw_deg

    async def Get_flight_mode(self) -> None:
        async for flight_mode in self.telemetry.flight_mode():
            self.Flight_mode = flight_mode

    async def Get_status_text(self) -> None:
        async for status_text in self.telemetry.status_text():
            self.Status_text = status_text
            
    async def Get_mission_progress(self): 
        async for mission_progress in self.mission.mission_progress():
            progress = f"Mission progress:{mission_progress.current}/"+ f"{mission_progress.total}"
            self.Mission_progress = progress
            
    async def Get_landed_State(self) -> None:#着地判定
        async for landed_state in self.telemetry.landed_state():
            # print(str(landed_state))
            self.Landed_state = landed_state
            
    async def Get_pressure(self) ->None:
        async for pressure in self.telemetry.scaled_pressure():
            self.Pressure = pressure.absolute_pressure_hpa

    async def Get_tempreture(self) ->None:
        async for imu in self.telemetry.imu():
            self.Temperature = imu.temperature_degc
            
    async def Get_acceleration_frd(self):
        async for imu in self.telemetry.imu():
            self.a_x = imu.acceleration_frd.forward_m_s2
            self.a_y = imu.acceleration_frd.right_m_s2
            self.a_z = imu.acceleration_frd.down_m_s2
            
    async def Get_odometry(self) -> None:
        """get odometery"""
        async for odometry in self.telemetry.odometry():
            self.X_m = odometry.position_body.x_m
            self.Y_m = odometry.position_body.y_m
            self.Z_m = odometry.position_body.z_m
            self.X_m_s = odometry.velocity_body.x_m_s
            self.Y_m_s = odometry.velocity_body.y_m_s
            self.Z_m_s = odometry.velocity_body.z_m_s
            self.Odometry_roll_rad_s = odometry.angular_velocity_body.roll_rad_s
            self.Odometry_pitch_rad_s = odometry.angular_velocity_body.pitch_rad_s
            self.Odometry_yaw_rad_s = odometry.angular_velocity_body.yaw_rad_s

    async def send_status_text(self, msg: int) -> None:
        """
        msg: messageの種類
          * 1はINFO
          * 他にもALERTとかERRORとかある
        """
        msg_type = server_utility.StatusTextType(5)
        await self.server_utility.send_status_text(msg_type, msg)


###action##########################################################################################
    async def Arm(self) -> None:
        """arm"""
        if str(self.Flight_mode) == "TAKEOFF":
            logger_info.info("Flight mode is TAKEOFF.")
            return
        logger_info.info("--Arming")
        await self.action.arm()

    async def Disarm(self) -> None:
        """disarm"""
        logger_info.info("--Disarming")
        await self.action.disarm()

    async def Hold(self) -> None:
        """hold"""
        logger_info.info("--Holding")
        await self.action.hold()

    async def Takeoff(self) -> None:
        """takeoff"""
        logger_info.info("--Taking off")
        await self.action.takeoff()

    async def Land(self) -> None:
        """land"""
        logger_info.info("--Landing")
        await self.action.land()

    async def Reboot(self) -> None:
        """reboot"""
        logger_info.info("--Reboot")
        await self.action.reboot()

    async def Shutdown(self) -> None:
        """shutdown"""
        logger_info.info("--Shutdown")
        await self.action.shutdown()

    async def Kill(self) -> None:
        """kill"""
        logger_info.info("--Kill")
        await self.action.kill()
        
    async def Return_to_launch(self) -> None:
        """return to launch site"""
        await self.action.return_to_launch()
        
    async def Upload_mission(self,mission_plan) -> None:
        logger_info.info("-- Uploading mission")
        await self.mission.upload_mission(mission_plan)
    
    async def Start_mission(self) -> None:
        logger_info.info("--Start mission")
        await self.mission.start_mission()
        
    async def Goto_location(
        self,
        latitude_deg: float,
        longitude_deg: float,
        absolute_altitude_m: float,
        yaw_deg: float,
    ) -> None:
        """go to the input location

        Args:
            latitude_deg (float): latitude in deg
            longitude_deg (float): longitude in deg
            absolute_altitude_m (float): absolute altitude in meter
            yaw_deg (float): yaw in deg
        """
        logger_info.info(
            "--Go to location to lat: "
            + str(latitude_deg)
            + " lng:"
            + str(longitude_deg)
            + " alt:"
            + str(absolute_altitude_m)
            + " yaw:"
            + str(yaw_deg)
        )
        await self.action.goto_location(
            latitude_deg, longitude_deg, absolute_altitude_m, yaw_deg
        )
        
    async def Do_orbit(self, radius, velocity, yaw, latitude, longitude, altitude):
        logger_info.info("do orbit"
                         +f"radius :{radius}"
                         +f"velocity: {velocity}"
                         +f"yaw :{yaw}"
                         +f"latitude :{latitude}"
                         +f"longitude :{longitude}"
                         +f"altitude :{altitude}")
        await self.action.do_orbit(radius_m=radius,
                                   velocity_ms=velocity,
                                   yaw_behavior=yaw,
                                   latitude_deg=latitude,
                                   longitude_deg=longitude,
                                   absolute_altitude_m=altitude)
            
        
    async def task_land(self):
        while True:
            if str(self.Flight_mode) != "LAND":
                try:
                    await self.Land()
                except mavsdk.action.ActionError:
                    logger_info.error("land ActionError")
                    await asyncio.sleep(0.1)
            else:
                break


    async def Set_takeoff_altitude(self, takeoff_altitude: float) -> None:
        """set takeoff altitude in m

        Args:
            takeoff_altitude (float): takeoff altitude [m]
        """
        self.takeoff_altitude = takeoff_altitude
        await self.action.set_takeoff_altitude(takeoff_altitude)
        
###offboard#####################################################################################
    async def Start_offboard(self) -> None:
        await self.offboard.start()
        logger_info.info("--Starting offboard")
    
    async def Move_offboard(self, forward, right, down, yaw):###R:ヨー角速度
        logger_info.info(f"move offboard"
                         +f"foward :{forward}"
                         +f"right :{right}"
                         +f"down :{down}"
                         +f"yaw :{yaw}")
        await self.offboard.set_velocity_body(
            VelocityBodyYawspeed(forward, right, down, yaw)
        )
        
###loop#########################################################################################
    async def Loop_hold_wait(self):
        logger_info.info("waiting for pixhawk to hold")
        flag = False
        while True:
            if flag==True:
                break
            async for flight_mode in self.telemetry.flight_mode():
                if str(flight_mode) == "HOLD":
                    logger_info.info("-- Hold")
                    flag=True
                    break
                else:
                    try:
                        await self.Hold()
                    except Exception as e:
                        logger_info.error(e)
                        # await self.Connect(system_address)
                        break 
                time.sleep(1)
                    
    async def Loop_arm_wait(self):
        logger_info.info("waiting for pixhawk to arm")
        flag = False
        while True:
            if flag==True:
                break
            async for armed in self.telemetry.armed():
                print(armed)
                if armed:
                    logger_info.info("-- Arm")
                    flag=True
                    break
                else:
                    try:
                        await self.Arm()
                    except Exception as e:
                        logger_info.error(e)
                        break
                time.sleep(1)

    async def Loop_takeoff_wait(self):
        logger_info.info("waiting for pixhawk to takeoff")
        flag = False
        while True:
            if flag==True:
                break
            async for flight_mode in self.telemetry.flight_mode():
                if str(flight_mode) == "TAKEOFF":
                    logger_info.info("-- Takeoff")
                    flag=True
                    break
                else:
                    try:
                        await self.Takeoff()
                    except Exception as e:
                        logger_info.error(e)
                        break
                    
    async def Loop_offboard_wait(self) ->None:
        logger_info.info("waiting for pixhawk to offboard")
        while True:    
            try:
                await self.Start_offboard()
                break
            except OffboardError as e:
                logger_info.error(e)
                logger_info.error(e._result.result)
                await self.Hold()
                continue


    async def Loop_position(self) -> None:
        while True:
            await self.Get_position()
            await asyncio.sleep(0.01)
        
    async def Loop_atitude(self) -> None:
        while True:
            await self.Get_attitude_angle()
            await asyncio.sleep(0.01)
    
    async def Loop_gpsinfo(self) -> None:
        while True:
            await self.Get_gps_info()
            await asyncio.sleep(0.01)


    async def Loop_lidar(self):
        while True:
            await self.Get_lidar()
            await asyncio.sleep(0.01)

    async def Loop_flight_mode(self):
        while True:
            await self.Get_flight_mode()
            await asyncio.sleep(0.01)
    
    async def Loop_landed_state(self):
        while True:
            print(self.Landed_state) 
            await asyncio.sleep(2)
            
    async def Loop_mission_progress(self):
        while True:
            await self.Get_mission_progress()
            logger_info.info(str(self.Mission_progress))
            await asyncio.sleep(1)

    async def Loop_status_text(self):
        while True:
            await self.Get_status_text()
            logger_info.info(str(self.Status_text))
            await asyncio.sleep(1)
            
    async def Loop_pressure(self) ->None:
        while True:
            await self.Get_pressure()
            # logger_info.info(str(self.Pressure))
            await asyncio.sleep(0.01)
            
    async def Loop_temperature(self):
        while True:
            await self.Get_tempreture()
            await asyncio.sleep(0.01)
            
    async def Loop_acceleration_frd(self):
        while True:
            await self.Get_acceleration_frd()
            await asyncio.sleep(0.01)
    
    async def Loop_odometry(self):
        while True:
            await self.Get_odometry()
            await asyncio.sleep(0.01)
    
    async def Loop_log(self) -> None:
        while True:
            mode = str(self.Flight_mode)
            dist = str(self.Lidar)[0:9]
            lat=str(self.Latitude_deg)[0:9]
            lon=str(self.Longitude_deg)[0:9]
            abs_alt=str(self.Absolute_altitude_m)[0:9]
            rel_alt=str(self.Relative_altitude_m)[0:9]
            logger_info.info(log_format(message = mode,
                                        distance = float(dist),
                                        relative_altitude = float(rel_alt),
                                        absolute_altitude= float(abs_alt),
                                        latitude= float(lat),
                                        longitude= float(lon)))
        
            await asyncio.sleep(0.5)
            
    async def Loop_goto_location(self, latitude_target,
                                 longitude_target,
                                 altitude_target):
        await self.Goto_location(latitude_target,
                                  longitude_target,
                                  altitude_target,0)
        while abs(altitude_target - self.Absolute_altitude_m) > 0.3 or abs(latitude_target - self.Latitude_deg) > 1.0e-5 or abs(longitude_target - self.Longitude_deg) > 1.0e-5:
            await asyncio.sleep(0.01)
            

async def image_process(drone:Bee, camera:Camera, time_fin):#画像処理
    time_start = time.time()
    latitude_camera = drone.Latitude_deg
    longitude_camera = drone.Longitude_deg
    altitude_camera = drone.Absolute_altitude_m    
    await drone.Loop_offboard_wait()
    await drone.Move_offboard(0.0,0.0,0.0,0.0)
    try_count = 0
    while True:
        await drone.Loop_offboard_wait()
        await asyncio.sleep(0.5)
        await camera.take_pic()
        await camera.detect_center_cv()
        
        if time.time() - time_start > time_fin:
            logger_info.info("not found")
            await drone.Loop_goto_location(latitude_target=latitude_camera,
                                            longitude_target=longitude_camera,
                                            altitude_target=altitude_camera)
            return

        elif camera.percent < 0.005:
            logger_info.info("try again")
            await drone.Loop_goto_location(latitude_target=latitude_camera,
                                            longitude_target=longitude_camera,
                                            altitude_target=altitude_camera)
            await drone.Do_orbit(radius=try_count,
                                 velocity=0.1,
                                 yaw=0,
                                 latitude=latitude_camera,
                                 longitude=longitude_camera,
                                 altitude=altitude_camera)
            try_count +=1
            
        elif abs(camera.left) >= 0.1 or abs(camera.forward) >= 0.1 :
            logger_info.info("move")
            await drone.Move_offboard(camera.forward, -camera.left, 0.0, 0.0)

        else :
            logger_info.info("down")
            if drone.Lidar < 1:
                drone.offboard.stop()
                return
            await drone.Move_offboard(0.0, 0.0, 0.05, 0.0)
