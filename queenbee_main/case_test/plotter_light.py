import time
import pandas as pd
from datetime import datetime, timedelta
#from queenbee.logger_case import logger_info, log_file_r
import matplotlib.pyplot as plt

def lst_light():
    global timelst_1
    global lightlst
    global exchangedot
    global timelst_2
    timelst_1 = []
    lightlst = []
    exchangedot = []
    timelst_2 = []
    df = pd.read_csv(r'.\\log\\2023-06-25_logger\\787.csv')
    #df = pd.read_csv('./log/2023-06-25_logger/777.csv')
    for i in range(len(df)):
        if df.iloc[i]['Message'] == 'Outside' or  df.iloc[i]['Message'] == 'Storage' or df.iloc[i]['Message'] == 'Released':
            timelst_1.append(datetime.strptime(str(df.iloc[i]['Timeinfo'])[:19], '%Y-%m-%d %H:%M:%S'))
            lightlst.append(df.iloc[i]['Light'])
        elif df.iloc[i]['Message'] == 'Storage Succeeded' or df.iloc[i]['Message'] =='Release Succeeded':
            exchangedot.append(df.iloc[i+1]['Light'])
            timelst_2.append(datetime.strptime(str(df.iloc[i+1]['Timeinfo'])[:19], '%Y-%m-%d %H:%M:%S'))
    #time.sleep(2)

def plot_light():
    global timelst_1
    global lightlst
    global exchangedot 
    global timelst_2
    plt.plot(timelst_1,lightlst)
    plt.scatter(timelst_2,exchangedot,c = "r")
    plt.show()

if __name__ == "__main__":
    global timelst_1
    global timelst_2
    global lightlst    
    lst_light()
    # print(timelst_1)
    # print(lightlst)
    plot_light()
