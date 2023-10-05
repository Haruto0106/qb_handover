from matplotlib import pyplot as plt 
import pandas as pd
from datetime import datetime

df = pd.read_csv(r".\\log\\2023-09-14_logger\\020.csv")

print(df.head())

lightlst = []
timelst = []
judgelight = []
judgetime = []
judgelight2 = []
judgetime2 = []
for i in range(1390,len(df),1):
    if df.iloc[i]["Message"] == 'Judge Release:LL' or df.iloc[i]["Message"] == 'Judge Land:L' or df.iloc[i]["Message"] == 'Land':
        lightlst.append(float(df.iloc[i]["Disp Pressure"]))
        timelst.append(datetime.strptime(str(df.iloc[i]['Timeinfo'])[:19], '%Y-%m-%d %H:%M:%S'))
    
    if df.iloc[i]["Message"] == "Release Succeeded":
        judgelight.append(float(df.iloc[i+1]["Disp Pressure"]))
        judgetime.append(datetime.strptime(str(df.iloc[i+1]['Timeinfo'])[:19], '%Y-%m-%d %H:%M:%S'))

    if df.iloc[i]["Message"] == "Landing Succeeded":
        judgelight2.append(float(df.iloc[i-1]["Disp Pressure"]))
        judgetime2.append(datetime.strptime(str(df.iloc[i-1]['Timeinfo'])[:19], '%Y-%m-%d %H:%M:%S'))

fig, ax = plt.subplots()
ax.plot(timelst, lightlst, c = "b")
ax.scatter(judgetime, judgelight, c = "r", s = 50)
ax.scatter(judgetime2, judgelight2, c = "g", s = 50)
plt.show()