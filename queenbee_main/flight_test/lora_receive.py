import serial
import time
ser=serial.Serial('COM10',19200,timeout=1)

while not ser.is_open:
    print("port cannot open")
    ser.open()
    time.sleep(1)
print("port open")

    
try :
    while True:
        value = ser.readline().decode('ascii').rstrip(('\n'))
        if "Receive Data" in value:    
            id = value.index("Receive Data")
            value = value[id+12:]
            print(value)
        else:
            # print('failed')
            continue
        # print(value)
        
finally:
    ser.close()
    print("port closed")