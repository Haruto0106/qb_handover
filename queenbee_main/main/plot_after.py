from matplotlib import pyplot as plt 
import pandas as pd
from datetime import datetime

df = pd.read_csv(r".\\log\\2023-08-18_logger\\005.csv")

print(df.head())

lightlst = []
timelst = []
judgelight = []
judgetime = []
for i in range(len(df)):
    if df.iloc[i]["Message"] == 'Outside' or df.iloc[i]["Message"] == 'Storage':
        lightlst.append(df.iloc[i]["Light"])
        timelst.append(datetime.strptime(str(df.iloc[i]['Timeinfo'])[:19], '%Y-%m-%d %H:%M:%S'))
    
    if df.iloc[i]["Message"] == "Storage Succeeded":
        judgelight.append(df.iloc[i+1]["Light"])
        judgetime.append(datetime.strptime(str(df.iloc[i+1]['Timeinfo'])[:19], '%Y-%m-%d %H:%M:%S'))
        
fig, ax = plt.subplots()
ax.plot(timelst, lightlst, c = "b")
ax.scatter(judgetime, judgelight, c = "r", s = 50)
plt.show()