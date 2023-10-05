import time
import pandas as pd
from datetime import datetime, timedelta
#from queenbee.logger_case import logger_info, log_file_r
import matplotlib.pyplot as plt

# def plot_pressure():
#     global timelst
#     global pressurelst
#     while True:
#         timelst = []
#         pressurelst = []
#         df = pd.read_csv('./log'+ log_file_r)
#         for i in range(len(df)):
#             if df.iloc[i]['Message'] == 'Released' or df.iloc[i]['Message'] == 'Land':
#                 timelst.append(datetime.strptime(str(df.iloc[i]['Timeinfo'])[:19], '%Y-%m-%d %H:%M:%S'))
#                 pressurelst.append(df.iloc[i]['Pressure'])
#         time.sleep(2)

def lst_pressure():
    global timelst
    global pressurelst
    global exchangedot
    global timelst_1
    timelst = []
    pressurelst = []
    exchangedot = []
    timelst_1 = []
    df = pd.read_csv(r'.\\log\\2023-06-25_logger\\777.csv')
    #df = pd.read_csv('./log/2023-06-25_logger/777.csv')
    for i in range(len(df)):
        if df.iloc[i]['Message'] == 'Storage' or  df.iloc[i]['Message'] == 'Released' or df.iloc[i]['Message'] == 'Land':
            timelst.append(datetime.strptime(str(df.iloc[i]['Timeinfo'])[:19], '%Y-%m-%d %H:%M:%S'))
            pressurelst.append(df.iloc[i]['Pressure'])
        elif df.iloc[i]['Message'] == 'Release Succeeded':
            exchangedot.append(df.iloc[i+3]['Pressure'])
            timelst_1.append(datetime.strptime(str(df.iloc[i+3]['Timeinfo'])[:19], '%Y-%m-%d %H:%M:%S'))
    # print(df.iloc[16]['Message'])
        #time.sleep(2)

def plot_pressure():
    global timelst
    global pressurelst
    global exchangedot
    global timelst_1
    plt.plot(timelst,pressurelst)
    plt.scatter(timelst_1,exchangedot,c = "r")
    plt.show()

# def lst_storage_light():
#     global timelst_1
#     global lightlst
#     timelst_1 = []
#     lightlst = []
#     df = pd.read_csv(r'.\\log\\2023-06-25_logger\\777.csv')
#     #df = pd.read_csv('./log/2023-06-25_logger/777.csv')
#     for i in range(len(df)):
#         if df.iloc[i]['Message'] == 'Outside':
#             timelst_1.append(datetime.strptime(str(df.iloc[i]['Timeinfo'])[:19], '%Y-%m-%d %H:%M:%S'))
#             lightlst.append(df.iloc[i]['Light'])
#     #time.sleep(2)



if __name__ == "__main__":
    global timelst
    global pressurelst    
    lst_pressure()
    print(timelst)
    print(pressurelst)
    plot_pressure()