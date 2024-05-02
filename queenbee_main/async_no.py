
import time

def print_after_6s(): #6秒後にprint
    time.sleep(6)
    print("6秒後")

def print_after_5s(): #5秒後にprint
    time.sleep(5)
    print("5秒後")

def print_after_4s(): #4秒後にprint
    time.sleep(4)
    print("4秒後")

start = time.time() #開始時間
print_after_6s()
print_after_5s()
print_after_4s()
end = time.time() #終了時間
print(f"かかった時間：{end-start}")