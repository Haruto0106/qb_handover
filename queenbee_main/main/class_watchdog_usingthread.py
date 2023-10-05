from threading import Timer

class Watchdog(Exception):
    def __init__(self,timeout,after,post_process=None):
        self.timeout = timeout
        self.post_process = post_process if post_process is not None else self.default_post_process
        self.timer = Timer(self.timeout , self.post_process)
        self.timer.start()

    def reset(self):
        self.timer.cancel()
        self.timer = Timer(self.timeout , self.post_process)
        self.timer.start()

    def stop(self):
        self.timer.cancel()

    def default_post_process(self):
        raise self
    
    # 使い方
    # watchdog = Watchdog(時間)
    # try:
    #     行う処理
    # except Watchdog:
    #     例外処理
    # finally:
    #     watchdog.stop