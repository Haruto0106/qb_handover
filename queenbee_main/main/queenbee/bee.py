import asyncio
import datetime
import mavsdk
from mavsdk.mission import MissionItem,MissionPlan
import numpy as np
from mavsdk import server_utility
from queenbee.logger_drone import logger_info, log_format
from mavsdk.offboard import OffboardError, VelocityBodyYawspeed, PositionNedYaw
import time
from queenbee.camera2 import Camera
from numpy import linalg as la
import serial.tools.list_ports
# from queenbee.class_case import Case

Cir_eq = 40076500 #m
Cir_md = 40008600 #m


class Bee(mavsdk.System):
    def __init__(self):
        super().__init__()
        logger_info.info("Pixhawk initialized")
        # system address
        self.SYSTEM_ADDRESS = "serial:///dev/ttyACM0:115200"
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
        # mission finish
        self.Mission_finished = False
        # mission item
        self.Mission_items = []
        # pressure
        self.Pressure = 0.0
        # temperature
        self.Temperature = 0.0
        # case
        self.lat_case = 0.0
        self.lon_case = 0.0
        self.alt_case = 0.0
        
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
        
        # goto config 
        self.gotorange = 0.0
        
        # reboot
        self.Reboot_flag = False    

###setup######################################################################################
    async def Port_check(self):
        ports = serial.tools.list_ports.comports()
        dev_lst = []
        for port in ports:
            dev_lst.append(port.device)
        logger_info.info(dev_lst)
        
        if '/dev/ttyACM0' in dev_lst:
            logger_info.info("system_address: /dev/ttyACMO")
            self.SYSTEM_ADDRESS = "serial:///dev/ttyACM0:115200"
        if '/dev/ttyACM1' in dev_lst:
            logger_info.info("system_address: /dev/ttyACM1")
            self.SYSTEM_ADDRESS = "serial:///dev/ttyACM1:115200"

    
    async def Connect(self) -> None:
        logger_info.info("Waiting for drone to connect...")
        await self.connect(system_address=self.SYSTEM_ADDRESS)

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
            if self.Reboot_flag:
                return

    async def Get_position(self) -> None:
        async for position in self.telemetry.position():
            self.Latitude_deg = position.latitude_deg
            self.Longitude_deg = position.longitude_deg
            self.Absolute_altitude_m = position.absolute_altitude_m
            self.Relative_altitude_m = position.relative_altitude_m
            if self.Reboot_flag:
                return
            
    async def Get_gps_info(self) -> None:
        """get number of satellites and fix type"""
        async for gps_info in self.telemetry.gps_info():
            self.num_satellites = gps_info.num_satellites
            self.fix_type = gps_info.fix_type
            if self.Reboot_flag:
                return

    async def Get_attitude_angle(self) -> None:
        """get angle from sensors"""
        async for angle in self.telemetry.attitude_euler():
            self.Pitch_deg = angle.pitch_deg
            self.Roll_deg = angle.roll_deg
            self.Yaw_deg = angle.yaw_deg
            if self.Reboot_flag:
                return
            
    async def Get_flight_mode(self) -> None:
        async for flight_mode in self.telemetry.flight_mode():
            self.Flight_mode = str(flight_mode)
            if self.Reboot_flag:
                return

    async def Get_status_text(self) -> None:
        async for status_text in self.telemetry.status_text():
            self.Status_text = status_text
            logger_info.info(self.Status_text)
            if self.Reboot_flag:
                return
            
    async def Get_mission_progress(self): 
        async for mission_progress in self.mission.mission_progress():
            progress = f"Mission progress:{mission_progress.current}/"+ f"{mission_progress.total}"
            self.Mission_progress = progress
            if self.Reboot_flag:
                return
            if self.Mission_finished:
                return
            
    async def Get_landed_State(self) -> None:#着地判定
        async for landed_state in self.telemetry.landed_state():
            # print(str(landed_state))
            self.Landed_state = landed_state
            if self.Reboot_flag:
                return
            
    async def Get_pressure(self) ->None:
        async for pressure in self.telemetry.scaled_pressure():
            self.Pressure = pressure.absolute_pressure_hpa
            if self.Reboot_flag:
                return

    async def Get_tempreture(self) ->None:
        async for imu in self.telemetry.imu():
            self.Temperature = imu.temperature_degc
            if self.Reboot_flag:
                return

    async def Get_acceleration_frd(self):
        async for imu in self.telemetry.imu():
            self.a_x = imu.acceleration_frd.forward_m_s2
            self.a_y = imu.acceleration_frd.right_m_s2
            self.a_z = imu.acceleration_frd.down_m_s2
            if self.Reboot_flag:
                return
            
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
            if self.Reboot_flag:
                return


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
        
    async def Clear_mission(self):
        logger_info.info("--Clear mission")
        await self.mission.clear_mission()
        
    async def Download_mission(self):
        logger_info.info("--Downloading mission")
        mission_plan = await self.mission.download_mission()
        logger_info.info(mission_plan.mission_items)
        
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
            "--Go to lat: "
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
        
    async def Set_speed(self, speed):
        logger_info.info(f"--set speed {speed}m/s")
        await self.action.set_current_speed(speed_m_s=speed)
        
        
    async def Set_max_speed(self, speed):
        logger_info.info(f"--set max speed : {speed} m/s")
        await self.action.set_maximum_speed(speed=speed) 
               
###offboard#####################################################################################
    async def Start_offboard(self) -> None:
        await self.offboard.start()
        logger_info.info("--Starting offboard")
        
    async def Stop_offboard(self):
        await self.offboard.stop()
        logger_info.info("--Stopping offboard")
    
    async def Offboard_vel_body(self, forward, right, down, yaw):###R:ヨー角速度
        logger_info.info(f"move offboard"
                         +f"foward :{forward}"
                         +f"right :{right}"
                         +f"down :{down}"
                         +f"yaw :{yaw}")
        await self.offboard.set_velocity_body(
            VelocityBodyYawspeed(forward, right, down, yaw)
        )
    
    async def Offboard_pos_ned(self, north, east, down, yaw):###R:ヨー角速度
        logger_info.info(f"move offboard"
                         +f"north :{north}"
                         +f"east :{east}"
                         +f"down :{down}"
                         +f"yaw :{yaw}")
        await self.offboard.set_position_ned(
            PositionNedYaw(north_m=north, east_m=east, down_m=down, yaw_deg=yaw)
        )        
###loop#########################################################################################
    async def Loop_hold_wait(self):
        logger_info.info("waiting for pixhawk to hold")
        trycount = 0
        while True:
            if self.Flight_mode == "HOLD":
                logger_info.info("-- Hold")
                break
            else:
                try:
                    await self.Hold()
                    break
                except Exception as e:
                    if trycount >= 5:
                        self.Reboot_flag = True
                        return
                    logger_info.error(e)
                    trycount += 1
            await asyncio.sleep(1)
                    
    async def Loop_arm_wait(self):
        logger_info.info("waiting for pixhawk to arm")
        flag = False
        trycount = 0
        while True:
            if flag==True:
                break
            async for armed in self.telemetry.armed():
                # print(armed)
                if armed:
                    logger_info.info("-- Arm")
                    flag=True
                    break
                else:
                    try:
                        await self.Arm()
                    except Exception as e:
                        if trycount >= 5:
                            self.Reboot_flag = True
                            return
                        logger_info.error(e)
                        trycount += 1
                        break
            await asyncio.sleep(1)

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
            if self.Reboot_flag:
                return
                    
    async def Loop_offboard_start(self) ->None:
        logger_info.info("waiting for pixhawk to start offboard")
        while True:    
            try:
                await self.Start_offboard()
                break
            except OffboardError as e:
                logger_info.error(e)
                logger_info.error(e._result.result)
                await self.Hold()
                continue
            
    async def Loop_offboard_stop(self):
        logger_info.info("waiting for pixhawk to stop offboard")
        while True:
            try:
                await self.Stop_offboard()
                break
            except OffboardError as e:
                logger_info.error(e)
                logger_info.error(e._result.result)
                await self.Hold()
                continue
    
    async def Loop_mission_start(self) -> None:
        trycount = 0
        while True:
            try:
                await self.Start_mission()
                break
            except Exception as e:
                if trycount >=5:
                    self.Reboot_flag = True
                    return
                logger_info.info(e)
                trycount += 1
            await asyncio.sleep(1)
                

    async def Loop_position(self) -> None:
        while True:
            await self.Get_position()
            await asyncio.sleep(0.01)
            if self.Reboot_flag:
                return
        
    async def Loop_atitude(self) -> None:
        while True:
            await self.Get_attitude_angle()
            await asyncio.sleep(0.01)
            if self.Reboot_flag:
                return
    
    async def Loop_gpsinfo(self) -> None:
        while True:
            await self.Get_gps_info()
            await asyncio.sleep(0.01)
            if self.Reboot_flag:
                return

    async def Loop_lidar(self):
        while True:
            await self.Get_lidar()
            await asyncio.sleep(0.01)
            if self.Reboot_flag:
                return

    async def Loop_flight_mode(self):
        while True:
            await self.Get_flight_mode()
            await asyncio.sleep(0.01)
            if self.Reboot_flag:
                return
    
    async def Loop_landed_state(self):
        while True:
            print(self.Landed_state) 
            await asyncio.sleep(2)
            if self.Reboot_flag:
                return
    
    async def Loop_mission_progress(self):
        while True:
            await self.Get_mission_progress()
            await asyncio.sleep(0.01)
            if self.Reboot_flag:
                return        
            if self.Mission_finished:
                return
    
    async def Loop_print_progress(self):
        while True:
            # await self.Get_mission_progress()
            logger_info.info(str(self.Mission_progress))
            await asyncio.sleep(2)
            if self.Reboot_flag:
                return
            if self.Mission_finished:
                return

    async def Loop_status_text(self):
        while True:
            await asyncio.sleep(0.5)
            if self.Reboot_flag:
                return
            await self.Get_status_text()
            await asyncio.sleep(0.5)
            if self.Reboot_flag:
                return
            
    async def Loop_pressure(self) ->None:
        while True:
            await self.Get_pressure()
            # logger_info.info(str(self.Pressure))
            await asyncio.sleep(0.01)
            if self.Reboot_flag:
                return
            
    async def Loop_temperature(self):
        while True:
            await self.Get_tempreture()
            await asyncio.sleep(0.01)
            if self.Reboot_flag:
                return
            
    async def Loop_acceleration_frd(self):
        while True:
            await self.Get_acceleration_frd()
            await asyncio.sleep(0.01)
            if self.Reboot_flag:
                return
    
    async def Loop_odometry(self):
        while True:
            await self.Get_odometry()
            await asyncio.sleep(0.01)
            if self.Reboot_flag:
                return

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
            if self.Reboot_flag:
                return
            
    async def Loop_goto_location(self, latitude_target,
                                 longitude_target,
                                 altitude_target):
        await self.Goto_location(latitude_target,
                                  longitude_target,
                                  altitude_target,0)
        while abs(altitude_target - self.Absolute_altitude_m) > 0.3 or abs(latitude_target - self.Latitude_deg) > self.gotorange or abs(longitude_target - self.Longitude_deg) > self.gotorange:
            await asyncio.sleep(0.01)
            
    async def Loop_goto_location_reboot(self, latitude_target,
                                 longitude_target,
                                 altitude_target, start, reboot_time):
        await self.Goto_location(latitude_target,
                                  longitude_target,
                                  altitude_target,0)
        while abs(altitude_target - self.Absolute_altitude_m) > 1.0 or abs(latitude_target - self.Latitude_deg) > 1.0e-5 or abs(longitude_target - self.Longitude_deg) > 1.0e-5:
            await asyncio.sleep(0.01)
            if time.perf_counter() > start + reboot_time:
                self.Reboot_flag = True
                return            
            
    async def Mission_append(self, latitude_target, longitude_target, altitude_target):
        self.Mission_items.append(MissionItem(latitude_target,
                                              longitude_target,
                                              altitude_target,
                                              0,
                                              False,
                                              float('nan'),
                                              float('nan'),
                                              MissionItem.CameraAction.NONE,
                                              float('nan'),
                                              float('nan'),
                                              float('nan'),
                                              float('nan'),
                                              float('nan')))
            
    async def Precise_location(self, times): # 外れ値を除去した平均GPS位置
        logger_info.info("--locate positon")
        while True:
            counter = 0
            latlst = []
            lonlst = []
            altlst = []
            while counter < times:
                await asyncio.sleep(0.1)
                latitude = self.Latitude_deg
                longitude = self.Longitude_deg
                altitude = self.Absolute_altitude_m
                if latitude == 0.0 and longitude == 0.0:
                    continue
                latlst.append(latitude)
                lonlst.append(longitude)           
                altlst.append(altitude) 
                counter += 1
            current = np.array([outliers_mean(latlst),
                                outliers_mean(lonlst), 
                                outliers_mean(altlst)]) 
            if not np.count_nonzero(np.isnan(current)):
                break
        logger_info.info(f"locate {current}")
        return current
    
    async def Precise_land(self, camera:Camera, time_out, percent=0.005):#画像航法
        logger_info.info("--Precise land start")
        await self.Set_speed(speed=1)# m/s
        await self.Loop_hold_wait()
        time_start = time.perf_counter()
        start_position = await self.Precise_location(10) # スタート位置を記憶
        try_count = 0
        
        while self.Lidar > 5: # 一旦lidarが使える高度まで下がる
            logger_info.info("too high")
            start_position = start_position - np.array([0,0,0.5])
            await self.Loop_goto_location(latitude_target=start_position[0],
                                          longitude_target=start_position[1],
                                          altitude_target=start_position[2])

        remember_position = await self.Precise_location(10)
            
        while True: # ゴールを検出するまで上昇(上限20ｍ)
            await asyncio.sleep(1)
            await camera.take_pic()
            await camera.detect_center_cv() # ゴール検出
            logger_info.info(f"center:{camera.x},{camera.y}")
            logger_info.info(f"percent:{camera.percent}")
            if camera.percent >= percent : # 発見
                logger_info.info("--detect")
                break
            else: #発見出来なかったら、上昇
                logger_info.info("--not detect")
                current = await self.Precise_location(10)
                await self.Loop_goto_location(latitude_target=current[0],
                                            longitude_target=current[1],
                                            altitude_target=current[2] + 1)
                if self.Lidar >= 10: # 20m以上は危険なので、一旦スタート位置に戻る
                    await self.Loop_goto_location(latitude_target=start_position[0],
                                                longitude_target=start_position[1],
                                                altitude_target=start_position[2])

        while True: # 検出に成功したら、位置合わせに移行
            await asyncio.sleep(2)
            await self.Loop_hold_wait()
            current = await self.Precise_location(10)            
            if time.perf_counter() - time_start > time_out: # タイムアップ、スタート位置にgoto -> landへ
                logger_info.info("not found")
                await self.Loop_goto_location(latitude_target=start_position[0],
                                              longitude_target=start_position[1],
                                              altitude_target=start_position[2])
                return
            
            await camera.take_pic()
            await camera.detect_center_cv() # ゴール検出
            logger_info.info(f"file:{camera.pic_path[-7:]}")
            logger_info.info(f"center:{camera.x},{camera.y}")
            logger_info.info(f"percent:{camera.percent}")
            logger_info.info(f"yaw:{self.Yaw_deg} [deg]")
            yaw = self.Yaw_deg*np.pi/180
            
            height = self.Lidar
            if height >= 10: # 10m以上はlidar使えないので、GPSを信頼
                height = self.Relative_altitude_m
            
            if camera.percent < percent or not camera.detect: # ゴールロスト -> スタート位置に戻る
                logger_info.info("try again")
                await self.Loop_goto_location(latitude_target=remember_position[0],
                                              longitude_target=remember_position[1],
                                              altitude_target=remember_position[2])
                try_count +=1
                continue
            
            start_position = await self.Precise_location(10) # ゴール検知出来ているのでスタート位置更新
            
            r = np.array([[camera.x*height*camera.tan_x],
                          [camera.y*height*camera.tan_y]]) #機体軸における、目標地点との差(ｍ)
            rotate = np.array([[np.cos(yaw), -np.sin(yaw)],
                               [np.sin(yaw), np.cos(yaw)]])
            r_e = np.dot(rotate,r).flatten() #地面固定座標系における、目標地点との差(ｍ)
            
            # ### 陰を認識した後のコーン本体への補正はこんな感じ？
            # r_e = r_e + cone_g/np.tan(np.deg2rad(theta))*np.array([-np.sin(np.deg2rad(phi)),
            #                                                        np.cos(np.deg2rad(phi))])
            # ### theta 太陽の高度　phi　太陽の東からの角度
            
            logger_info.info(f"north:{r_e[0]}, east:{r_e[1]}")
            
            if la.norm(r_e) < 0.5: #十分近ければ50cm下降
                logger_info.info("down")
                if self.Lidar < 2.0: # 十分地面に近い -> landへ
                    logger_info.info("-- precise land end")
                    return

                await self.Loop_goto_location(latitude_target=start_position[0],
                                            longitude_target=start_position[1],
                                            altitude_target=start_position[2] - 1)
                # await self.Offboard_pos_ned(0, 0, 0, 0)  ###offboardで下降するならこっち
                # await self.Loop_offboard_start()
                # await self.Offboard_pos_ned(0, 0, 0.5, 0)
                # await asyncio.sleep(5)
                # await self.Loop_offboard_stop()
                continue
            
            else : # 検出地点へ移動
                logger_info.info("move")
                d_lat = r_e[0]/Cir_md*360 ##緯度差
                d_lon = r_e[1]/Cir_eq/np.cos(self.Latitude_deg*np.pi/180)*360 ##経度差  アメリカでは座標系が逆になる可能性があるので、ここにマイナスを付ける(多分大丈夫)
                error = np.array([d_lat,
                                  d_lon,
                                  0])        
                logger_info.info(f"lat{error[0]}, lon:{error[1]}")
                ##制御器
                target = error + start_position 
                if self.Lidar > 3:
                    await self.Loop_goto_location(latitude_target=target[0],
                                                    longitude_target=target[1],
                                                    altitude_target=target[2] -1 )

                else:
                    await self.Loop_goto_location(latitude_target=target[0],
                                            longitude_target=target[1],
                                            altitude_target=target[2] - 0.4)
        
        
            
def outliers_mean(lst):# 四分位範囲から外れ値を除いた平均を求める
    quartile_1, quartile_3 = np.percentile(lst, [25, 75])
    iqr = quartile_3 - quartile_1
    # 下限
    lower_bound = quartile_1 - (iqr * 1.5)
    # 上限
    upper_bound = quartile_3 + (iqr * 1.5)
    array = np.array(lst)[((lst > lower_bound) & (lst < upper_bound))]
    mean = np.average(array)
    return mean


def gps_distance(lat1, lon1, lat2, lon2):
    R = 6378137
    lat1 = np.deg2rad(lat1)
    lon1 = np.deg2rad(lon1)
    lat2 = np.deg2rad(lat2)
    lon2 = np.deg2rad(lon2)
    dist = R*np.arccos(np.sin(lat1)*np.sin(lat2) + np.cos(lat1)*np.cos(lat2)*np.cos(lon2-lon1))
    return dist # m
        