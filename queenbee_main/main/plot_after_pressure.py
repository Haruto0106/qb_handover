from matplotlib import pyplot as plt 
import pandas as pd
from datetime import datetime

df = pd.read_csv(r".\\log\\2023-09-14_logger\\020.csv")

print(df.head())

pressurelst = []
timelst = []
judgepressure = []
judgetime = []
judgepressure2 = []
judgetime2 = []
print(df.iloc[133])
for i in range(len(df)):
    if df.iloc[i]["Message"] == 'Judge Release:LL' or df.iloc[i]["Message"] == 'Released' or df.iloc[i]["Message"] == 'Judge Land:L' or df.iloc[i]["Message"] == 'Land':
        # if i == 132 or i == 134 or i == 135:
        #     continue
        # if i > 135:
        # else:
        pressurelst.append(float(df.iloc[i]["Pressure"]))
        timelst.append(datetime.strptime(str(df.iloc[i]['Timeinfo'])[:19], '%Y-%m-%d %H:%M:%S'))
        
    if df.iloc[i]["Message"] == "Landing Succeeded":
        judgepressure.append(df.iloc[i-1]["Pressure"])
        judgetime.append(datetime.strptime(str(df.iloc[i-1]['Timeinfo'])[:19], '%Y-%m-%d %H:%M:%S'))
        
    if df.iloc[i]["Message"] == "Release Succeeded":
        judgepressure2.append(df.iloc[i-1]["Pressure"])
        judgetime2.append(datetime.strptime(str(df.iloc[i-1]['Timeinfo'])[:19], '%Y-%m-%d %H:%M:%S'))

fig, ax = plt.subplots()
ax.plot(timelst, pressurelst, c = "b")
ax.scatter(judgetime, judgepressure, c = "r", s = 50)
ax.scatter(judgetime2, judgepressure2, c = "g", s = 50)
plt.show()