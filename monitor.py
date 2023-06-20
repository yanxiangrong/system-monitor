import sys
import time
from queue import Queue, Full
from threading import Thread

from pymongo.collection import Collection

from data_collection import system_status


class Monitor:
    def __init__(self, mongo_coll: Collection):
        self.mongo_coll = mongo_coll
        self.queue = Queue()

    def monitor_loop(self):
        while True:
            data = {
                'time': system_status.now_time(),
                'cpu': system_status.cpu(),
            }
            self.mongo_coll.insert_one(data)
            try:
                self.queue.put_nowait(data['time'])
            except Full:
                pass
            time.sleep(3)

    def run(self):
        try:
            self.monitor_loop()
        except Exception as e:
            sys.exit(e)
        sys.exit('monitor exit')

    def start(self):
        Thread(target=self.run, daemon=True).start()

    def wait_update(self):
        return self.queue.get()
