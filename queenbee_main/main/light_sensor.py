#必要なモジュールをインポート
import spidev                       #SPI通信用のモジュールをインポート
import time                         #時間制御用のモジュールをインポート
import sys                          #sysモジュールをインポート
import smbus


#連続して値を読み込む
while True:
    try:
        #SPI通信を行うための準備
        spi = spidev.SpiDev()               #インスタンスを生成
        spi.open(0, 0)                      #CE0(24番ピン)を指定
        spi.max_speed_hz = 1000000          #転送速度 1MHz

        resp = spi.xfer2([0x68, 0x00])                 #SPI通信で値を読み込む
        volume = ((resp[0] << 8) + resp[1]) & 0x3FF    #読み込んだ値を10ビットの数値に変換
        # print(f"Pressure:{}")
        time.sleep(1)                                  #1秒間待つ
        #I2C設定
        i2c = smbus.SMBus(1)#SMBusの引数に1を指定する。Raspberry Piのi2cバスの番号(見た感じ引数1でよさそう)
        address = 0x5d
        time.sleep(0.02)

        #Lセンサーの設定
        i2c.write_byte_data(address, 0x20, 0x90)
        time.sleep(0.02)
        
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
        print('Light'+ str(volume))
        print('Pressure: ' + str(prs))
        print('Temperature: ' + str(tmp))

        #一時停止
        time.sleep(1)

    except KeyboardInterrupt:
        #Ctrl+Cキーが押された
        spi.close()                            #SPI通信を終了
        sys.exit()                             #プログラム終了

    finally:
        spi.close()     
        # sys.exit()

