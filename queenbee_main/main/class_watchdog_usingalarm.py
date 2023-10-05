import signal

class Watchdog(Exception):
    def __init__(self, time):
        self.time = time

    def __enter__(self):
        signal.signal(signal.SIGALARM, self.post_process)
        signal.alarm(self.time)

    def __exit__(self , type , value , traceback):
        signal.alarm(0)
    
    def post_process(self , signum , frame):
        raise self
    

# try:
#     with Watchdog(5):
#         行う処理
# except Watchdog:
#     例外処理