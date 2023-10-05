import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import asyncio
import folium

timelst = []
lidarlst = []
df = pd.read_csv("011.csv")
for i in range(len(df)):
    if df.iloc[i]["Message"] == 'MANUAL' or df.iloc[i]["Message"] == 'HOLD' or df.iloc[i]["Message"] == 'LAND' or df.iloc[i]["Message"] == 'TAKEOFF':
        timelst.append(datetime.strptime(str(df.iloc[i]['Timeinfo'])[:19], '%Y-%m-%d %H:%M:%S'))
        lidarlst.append(df.iloc[i]["Distance"])
        
fig1 ,ax1 = plt.subplots()
suptime = timelst[-1]
inftime = suptime - timedelta(minutes=1)
suptime = suptime + timedelta(seconds= 5)    
ax1.set_xlim(inftime, suptime)

ax1.plot(timelst,lidarlst, color = 'b')
plt.show()
