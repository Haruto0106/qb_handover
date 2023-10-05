import asyncio
import datetime
import mavsdk
from mavsdk.mission import MissionItem,MissionPlan
import numpy as np
from mavsdk import server_utility
from queenbee.with_landedstate_logger import logger_info, log_format

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
        # landed state
        self.Landed_state = 0.0        
        # status_text
        self.Status_text = ""
        # mission progress
        self.Mission_progress = ""

###setup######################################################################################
    async def Connect(self, system_address: str) -> None:
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

    async def get_attitude_angle(self) -> None:
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


        
###loop#########################################################################################
    async def Loop_hold_wait(self, system_address: str):
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
                        await self.Connect(system_address)
                        break 
                    
    async def Loop_arm_wait(self):
        logger_info.info("waiting for pixhawk to arm")
        flag = False
        while True:
            if flag==True:
                break
            async for flight_mode in self.telemetry.flight_mode():
                if str(flight_mode) == "ARM":
                    logger_info.info("-- Arm")
                    flag=True
                    break
                else:
                    try:
                        await self.Arm()
                    except Exception as e:
                        logger_info.error(e)
                        break

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


    async def Loop_position(self) -> None:
        while True:
            await self.Get_position()
            await asyncio.sleep(1)

    async def Loop_lidar(self):
        while True:
            await self.Get_lidar()
            await asyncio.sleep(1)

    async def Loop_flight_mode(self):
        while True:
            await self.Get_flight_mode()
            await asyncio.sleep(1)
    
    async def Loop_landed_state(self):
        while True:
            print(self.Landed_state) 
            await asyncio.sleep(2)
            
    async def Loop_mission_progress(self):
        while True:
            logger_info.info(str(self.Mission_progress))
            await asyncio.sleep(1)

    async def Loop_status_text(self):
        while True:
            await self.Get_status_text()
            logger_info.info(str(self.Status_text))
            await asyncio.sleep(1)
            
    async def Loop_log_with_landedstate(self) -> None:
        while True:
            mode = str(self.Flight_mode)
            dist = str(self.Lidar)[0:9]
            lat=str(self.Latitude_deg)[0:9]
            lon=str(self.Longitude_deg)[0:9]
            abs_alt=str(self.Absolute_altitude_m)[0:9]
            rel_alt=str(self.Relative_altitude_m)[0:9]
            landmode = str(self.Landed_state)
            logger_info.info(log_format(message = mode,
                                        distance = float(dist),
                                        relative_altitude = float(rel_alt),
                                        absolute_altitude= float(abs_alt),
                                        latitude= float(lat),
                                        longitude= float(lon),
                                        landedstate= landmode))
            await asyncio.sleep(0.5)
            
