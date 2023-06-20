import sys
import time
from threading import Thread

from pymongo.collection import Collection

from data_collection import system_status


class Monitor:
    def __init__(self, mongo_coll: Collection):
        self.mongo_coll = mongo_coll

    def monitor_loop(self):
        while True:
            data = {
                'time': system_status.now_time(),
                'cpu': system_status.cpu(),
            }
            self.mongo_coll.insert_one(data)
            time.sleep(3)

    def run(self):
        try:
            self.monitor_loop()
        except Exception as e:
            sys.exit(e)
        sys.exit('monitor exit')

    def start(self):
        Thread(target=self.run, daemon=True).start()
