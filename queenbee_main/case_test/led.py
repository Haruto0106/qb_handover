#LED1個でLチカ
#テスト用
import RPi.GPIO as GPIO
import time

pin_no = 17 # 抵抗に繋いだ側の、GPIOポート番号

GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_no, GPIO.OUT)

for i in range(15):
    GPIO.output(pin_no, GPIO.HIGH) # 点灯
    time.sleep(0.4)
    GPIO.output(pin_no, GPIO.LOW) # 消灯
    time.sleep(0.4)

GPIO.cleanup()
