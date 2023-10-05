import serial
ser=serial.Serial('COM10',19200,timeout=1)

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
    
    
