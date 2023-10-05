from matplotlib import pyplot as plt 
import pandas as pd
from datetime import datetime

df = pd.read_csv(r".\\log\\2023-09-14_logger\\034.csv")

print(df.head())

lightlst = []
timelst = []
judgelight = []
judgetime = []
judgelight2 = []
judgetime2 = []
for i in range(len(df)):
    timelst.append(datetime.strptime(str(df.iloc[i]['Timeinfo'])[:19], '%Y-%m-%d %H:%M:%S'))
    if df.iloc[i]["Message"] == 'Judge Storage:L' or df.iloc[i]["Message"] == 'Judge Release:LL':
        lightlst.append(float(df.iloc[i]["Distance"]))
    
    if df.iloc[i]["Message"] == "Storage Succeeded":
        judgelight.append(float(df.iloc[i-1]["Distance"]))
        judgetime.append(datetime.strptime(str(df.iloc[i-1]['Timeinfo'])[:19], '%Y-%m-%d %H:%M:%S'))

    if df.iloc[i]["Message"] == "Release Succeeded":
        judgelight2.append(float(df.iloc[i-1]["Distance"]))
        judgetime2.append(datetime.strptime(str(df.iloc[i-1]['Timeinfo'])[:19], '%Y-%m-%d %H:%M:%S'))
        
disppressurelst = []
judgepressure = []
judgepressure2 = []
for i in range(len(df)):
    if df.iloc[i]["Message"] == 'Judge Release:LL' or df.iloc[i]["Message"] == 'Judge Land:L' or df.iloc[i]["Message"] == 'Land':
        disppressurelst.append(float(df.iloc[i]["Absolute Altitude"]))
    
    if df.iloc[i]["Message"] == "Release Succeeded":
        judgepressure.append(float(df.iloc[i+1]["Absolute Altitude"]))
        judgetime.append(datetime.strptime(str(df.iloc[i+1]['Timeinfo'])[:19], '%Y-%m-%d %H:%M:%S'))

    if df.iloc[i]["Message"] == "Landing Succeeded":
        judgepressure2.append(float(df.iloc[i-1]["Absolute Altitude"]))
        judgetime2.append(datetime.strptime(str(df.iloc[i-1]['Timeinfo'])[:19], '%Y-%m-%d %H:%M:%S'))
    
fig, ax = plt.subplots()
ax.plot(timelst, lightlst, c = "b")
ax.plot(timelst, disppressurelst, c = "orange")
ax.scatter(judgetime, judgelight, c = "r", s = 50)
ax.scatter(judgetime2, judgelight2, c = "g", s = 50)
plt.show()