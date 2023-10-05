import smbus
import time

#I2C設定
i2c = smbus.SMBus(1)#SMBusの引数に1を指定する。Raspberry Piのi2cバスの番号(見た感じ引数1でよさそう)
address = 0x5d
print("i2c start")
time.sleep(1)

#Lセンサーの設定
i2c.write_byte_data(address, 0x20, 0x90)
time.sleep(1)
print("sensor detected")

#ファイルオープン（書き込みモード）
f = open("lps25hb.csv", "w")
time.sleep(1)

#10回繰り返す
for i in range(10):
    
    #データ読み込み
    pxl = i2c.read_byte_data(address, 0x28)
    pl = i2c.read_byte_data(address, 0x29)
    ph = i2c.read_byte_data(address, 0x2A)
    tl = i2c.read_byte_data(address, 0x2B)
    th = i2c.read_byte_data(address, 0x2C)
    
    #データ変換
    prs = ph << 16 | pl << 8 | pxl
    tmp = th << 8 | tl
    
    #極性判断(温度)
    if tmp >= 32768:
        tmp -= 65536
    
    #物理量に変換
    prs = prs / 4096
    tmp = 42.5 + tmp / 480
    
    #表示
    print('Pressure: ' + str(prs))
    print('Temperature: ' + str(tmp))
    
    #データのCSV変換とファイルへの書き込み
    f.write(str(i + 1) + ',' + str(prs) + ',' + str(tmp) + '\n')
    
    #一時停止
    time.sleep(1)

f.close()