import asyncio
import time

async def print_after_6s(): #6秒後にprint
    await asyncio.sleep(6)
    print("6秒後")

async def print_after_5s(): #5秒後にprint
    await asyncio.sleep(5)
    print("5秒後")

async def print_after_4s(): #4秒後にprint
    await asyncio.sleep(4)
    print("4秒後")

async def main():
    start = time.time() #開始時間
    task1 = asyncio.create_task(print_after_6s())
    task2 = asyncio.create_task(print_after_5s())
    task3 = asyncio.create_task(print_after_4s())
    await task1
    await task2
    await task3
    end = time.time() #終了時間
    print(f"かかった時間：{end-start}")

asyncio.run(main()) #実行