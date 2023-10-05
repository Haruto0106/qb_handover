from queenbee.logger import logger_info, log_file_r
# import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import asyncio
import folium

async def df_lidar():
    global timelst
    global lidarlst
    while True:
        timelst = []
        lidarlst = []
        df = pd.read_csv('./log'+ log_file_r)
        for i in range(len(df)):
            if df.iloc[i]["Message"] == 'MANUAL' or df.iloc[i]["Message"] == 'HOLD' or df.iloc[i]["Message"] == 'LAND' or df.iloc[i]["Message"] == 'TAKEOFF':
                timelst.append(datetime.strptime(str(df.iloc[i]['Timeinfo'])[:19], '%Y-%m-%d %H:%M:%S'))
                lidarlst.append(df.iloc[i]["Distance"])
        await asyncio.sleep(2)

async def df_GPS():
    global latlst
    global lonlst
    while True:
        latlst = []
        lonlst = []
        df = pd.read_csv('./log'+ log_file_r)
        for i in range(len(df)):
            if df.iloc[i]["Message"] == 'MANUAL' or df.iloc[i]["Message"] == 'HOLD' or df.iloc[i]["Message"] == 'LAND' or df.iloc[i]["Message"] == 'TAKEOFF':
                latlst.append(df.iloc[i]["Latitude"])
                lonlst.append(df.iloc[i]["Longitude"])
        await asyncio.sleep(2)

async def plot_lidar():
    global timelst
    global lidarlst
    fig1 ,ax1 = plt.subplots()
    while True:
        try:
            suptime = timelst[-1]
            inftime = suptime - timedelta(minutes=1)
            suptime = suptime + timedelta(seconds= 5)    
            ax1.set_xlim(inftime, suptime)

            ax1.plot(timelst,lidarlst, color = 'b')
            plt.pause(2)
            plt.cla()
            await asyncio.sleep(2)
        except Exception as e:
            logger_info.warning(e)
            await asyncio.sleep(2)
            continue
        


async def plot_GPS():
    global latlst
    global lonlst
    fig2 ,ax2 = plt.subplots()
    while True:
        try:
            ax2.plot(timelst,lidarlst, color = 'r')
            plt.pause(2)
            plt.cla()
            await asyncio.sleep(2)
        except Exception as e:
            logger_info.warning(e)
            await asyncio.sleep(2)
            continue

async def map_GPS():
    global latlst
    global lonlst
    while True:
        try:
            startlat = latlst[0]
            startlon = lonlst[0]
            endlat = latlst[-1]
            endlon = lonlst[-1]
            m=folium.Map(location=[startlat,startlon],zoom_start=20)
            folium.Marker([startlat,startlon],popup='Start',
                          icon=folium.Icon(color="blue", icon="flag")).add_to(m)
            folium.Marker([endlat,endlon],popup='Drone',
                          icon=folium.Icon(color="red", icon="plane")).add_to(m)        
            sq = [
                (latlst[i], lonlst[i])
                for i in range(len(latlst))
            ]
            folium.PolyLine(locations=sq).add_to(m)    
            m.save('./log'+ log_file_r[:22] + '.html')
            await asyncio.sleep(2)
        except Exception as e:
            logger_info.warning(e)
            await asyncio.sleep(2)
            continue
        
        
async def plot_position():
    global timelst
    global lidarlst
    global latlst
    global lonlst

    fig = plt.figure(figsize=(12,6))
    ax1 = fig.add_subplot(1,2,1)
    ax2 = fig.add_subplot(1,2,2)
    while True:
        try:
            suptime = timelst[-1]
            inftime = suptime - timedelta(minutes=1)
            suptime = suptime + timedelta(seconds= 5)    

            ax1.set_xlim(inftime, suptime)
            ax1.plot(timelst,lidarlst, color = 'b')
            
            startlat = latlst[0]
            startlon = lonlst[0]

            ax2.set_xlim(startlat-0.001,startlat+0.001)
            ax2.set_ylim(startlon-0.001,startlon+0.001)            
            ax2.plot(latlst,lonlst, color = 'r')


            plt.pause(2)
            plt.cla()
            await asyncio.sleep(2)
        except Exception as e:
            logger_info.warning(e)
            await asyncio.sleep(2)
            continue