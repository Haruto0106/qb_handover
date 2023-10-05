from queenbee.mapping import ChromeOption, Google_map
import time
from datetime import datetime
import serial
import re

###注意###
#必ず使う前にすべてのchromeを閉じること！！！#

def host_receive(ser:serial.Serial):
    value = ser.readline().decode('ascii').rstrip(('\n'))
    if "Receive Data" in value:    
        id = value.index("Receive Data")
        value = value[id+12:]
        print(value)
        lst = re.findall(r'[-+]?\d*\.\d+|\d+',value)
        # 現在の時刻を取得
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file_path, "w") as log_file:
        
            # データとタイムスタンプをログファイルに書き込む
            log_file.write(f"{current_time}: {value}\n")
            log_file.flush()  # ファイルを即座に書き込む
        return lst
    else:
        return []



if __name__ == "__main__":
    while True:
        usr = input("username:")
        if usr == "hideshima":
            chromepath = "\\Users\\taiko\\AppData\\Local\\Google\\Chrome\\User Data" 
            profilename = "Profile 7"
            portname = 'COM10'
            break

        elif usr == "nomura":
            chromepath = "\\Users\\toshi\\AppData\\Local\\Google\\Chrome\\User Data"
            profilename = "Profile 2"
            portname = "COM6"
            break
        
        elif usr == "tanaka":
            chromepath = "\\Users\\tj-ha\\AppData\\Local\\Google\\Chrome\\User Data"
            profilename = "Profile 4"
            portname = "COM9"
            break
        
        else :
            print("No such user")

    filename = str(datetime.today())
    options = ChromeOption(chromepath=chromepath, profilename=profilename)
    driver = Google_map(options=options)
    driver.connect_map(filename=filename)
    
    ser=serial.Serial(portname,19200,timeout=None)##COMportは人によって違う
    
    while not ser.is_open:
        print("port cannot open")
        ser.open()
    print("port open") 
    
    log_folder = ".\\lora_log"
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file_path = f"{log_folder}\\serial_log_{timestamp}.txt"
    
    try:
        while True:
            position = host_receive(ser)
            if position:
                driver.plot(lat=position[0], lon=position[1])            
    finally:
        ser.close()
        print("port closed")
        driver.close()
