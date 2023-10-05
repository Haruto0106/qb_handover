import os
import sys
import mavsdk
import mavsdk.action 
from queenbee.bee import Bee
import RPi.GPIO as GPIO
import serial
import time
from queenbee.class_case import Case

sys.path.append(os.getcwd())
import asyncio
import struct


class Lora:
    def __init__(self):
        # pin number
        # reset
        self.rst = 17
        # Vin
        self.power = 4

        # 改行文字
        self.CRLF = "\r\n"
        # massage received from PC on ground
        self.msg_received = "hello, world"

        # serial
        self.serial = serial.Serial("/dev/ttyS0", 19200, timeout=1)

        # power
        self.is_on = False
        # is out of carrier?
        self.is_out = False
        #         self.is_sending = False
        
        self.counter = 0

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.rst, GPIO.OUT)
        GPIO.setup(self.power, GPIO.OUT)

    async def power_off(self) -> None:
        """cut power for lora"""
        GPIO.output(self.power, GPIO.LOW)
        self.is_on = False
        await asyncio.sleep(1)

    async def power_on(self):
        """start lora"""
        GPIO.output(self.power, GPIO.HIGH)

        GPIO.output(self.rst, GPIO.LOW)
        await asyncio.sleep(2)
        GPIO.output(self.rst, GPIO.HIGH)
        await asyncio.sleep(2)
        print("lora power on")
        #await self.write("processor")
        await self.write("start")

        self.is_on = True

    async def write(self, message: str) -> None:
        """write lora

        Args:
          massage (str): command or massage to send
        """
        #         self.is_sending = True
        msg_send = str(message) + self.CRLF
        self.serial.write(msg_send.encode("ascii"))
        await asyncio.sleep(4)

    #         self.is_sending = False

    async def read(self) -> None:
        """clear header and read lora"""
        data = self.serial.readline()
        fmt = "4s4s4s" + str(len(data) - 14) + "sxx"  # rssi, rcvidが両方onの時のヘッダー除去

        try:
            line = struct.unpack(fmt, data)
            self.msg_received = line[3].decode("ascii")
            await asyncio.sleep(1)
        except struct.error:
            await asyncio.sleep(1)

    async def close(self) -> None:
        """close serial connection"""
        self.serial.close()

    async def check_gps(self, drone: Bee) -> None:###GPS数7以上、高度2000mで放出判定するコードだけど、落下中ってpixhawkとLora使えるのか疑問
        """check num_satellites and absolute_altitude_m and judge if drone is out of carrier"""
        if drone.num_satellites > 6:
            if drone.Absolute_altitude_m > 2000:
                self.is_out = True
        await asyncio.sleep(1) 

    async def switch_lora(self, drone:Bee):###放出判定でLoraのスイッチオン
        """turn off lora until drone is out of carrier"""
        while True:
            await self.check_gps(drone)
            if self.is_out:
                await self.power_on()
                return
            await self.power_off()

    async def cycle_send_position(self, drone:Bee):
        while True:
            if self.is_on:
                position = f"lat:{str(drone.Latitude_deg)[0:9]},lng:{str(drone.Longitude_deg)[0:9]},alt:{str(drone.Absolute_altitude_m)[0:9]}"
                print(f"send position{position}")
                # await self.write(lat)
                # await self.write(lng)
                # await self.write(alt)
                await self.write(position)
            await asyncio.sleep(10)  # this must be a little long because lora cannot receive message while sending
    
    async def cycle_send(self):
        while True:
            if self.is_on:
                print("send ", self.counter)
                await self.write(self.counter)
                self.counter += 1
            await asyncio.sleep(10)
        
    async def cycle_send_case_position(self, drone:Bee):
        await asyncio.sleep(5)
        while True:
            if self.is_on:
                case_position = f"lat:{str(drone.lat_case)[0:9]},lng:{str(drone.lon_case)[0:9]}"
                print(f"send case position{case_position}")
                await self.write(case_position)
            await asyncio.sleep(10)
#droneとcaseのpositionは同関数で送った方がいいかも######################

    async def cycle_send_all_position(self, drone:Bee):
        while True:
            if self.is_on:

                position = f"lat:{str(drone.Latitude_deg)[0:9]},lng:{str(drone.Longitude_deg)[0:9]},lidar:{str(drone.Lidar)[0:4]}"
                print(f"send position{position}")
                await self.write(position)
                await asyncio.sleep(5)

                case_position = f"lat:{str(drone.lat_case)[0:9]},lng:{str(drone.lon_case)[0:9]}"
                print(f"send case position{case_position}")
                await self.write(case_position)
                await asyncio.sleep(5)
            if drone.Reboot_flag:
                return
                
#####################################################################            
    async def cycle_receive_lora(self, drone:Bee):
        while True:
            #             while True:
            #                 if not self.is_sending:
            #                     break;
            #                 await asyncio.sleep(0.01)
            await self.read()
            print("msg_received:", self.msg_received)
            if self.msg_received == "kill":
                try:
                    await drone.Kill()
                except mavsdk.action.ActionError:
                    self.msg_received = "hello, world"

            if self.msg_received == "land":
                try:
                    await drone.Land()
                except mavsdk.action.ActionError:
                    self.msg_received = "hello, world"
            await asyncio.sleep(1)

    #Caseのシーケンスメッセージ送信用（threadの中で動かす）######################################
    #nseで使用したもの（動くけどエラー出る）     
    async def cycle_send_progress(self,case_:Case):
        while case_.FINISHCASE == False:
            progress = f"progress:{str(case_.message)}"
            print(f"send progress{progress}")
                # await self.write(lat)
                # await self.write(lng)
                # await self.write(alt)
            await self.write(progress)
            await asyncio.sleep(5)
        return
    
    def do_cycle_send_progress(self,case_:Case):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.cycle_send_progress(case_))
        loop.close()

    def do_async(self,case_:Case):
        asyncio.run(self.do_cycle_send_progress(case_))

    #改良
    def write2(self,message:str) -> None:
        msg_send2 = str(message) + self.CRLF
        self.serial.write(msg_send2.encode("ascii"))
        time.sleep(0.1)

    def cycle_send_progress2(self,case_:Case):
        while case_.FINISHCASE == False:
            progress = f"progress:{str(case_.message)}"
            print(f"send progress{progress}")
            self.write2(progress)
            time.sleep(5)
        return         