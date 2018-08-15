"""
    Check the functionality of a proxy
"""

from proxy_pool import db
from proxy_pool import settings
from proxy_pool.db import Proxy

from datetime import datetime
from queue import Queue
import threading
import requests
import json

class MasterThread(threading.Thread):
    """ Get proxy from mongodb to exam """

    def __init__(self, queue):
        self.queue = queue
        super().__init__()

    def run(self):
        """ sort by count (descend) then by update_time (ascend)
        so it removes bad ones more efficiently
        """
        while True:
            for proxy in Proxy.aggregate([{ "$sort" : { "count": -1, "update_time": 1 } }]):
                self.queue.put(proxy)


class SlaveThread(threading.Thread):
    """ Check if the proxy works """

    def __init__(self, queue, master):
        self.queue = queue
        super().__init__()

    def run(self):
        while True:
            proxy = self.queue.get()
            proxy.status('check')
            if proxy.count < settings.DEL_SIGNAL:
                if self.check(proxy):  # success
                    proxy.count = 0 
                    proxy.status('success')
                else:
                    proxy.count += 1
                    proxy.status('fail')
                proxy.update_time = datetime.now() 
                proxy.save()
            else:
                proxy.status('delete')
                proxy.delete()                
            self.queue.task_done()

    def check(self, proxy):
        try:
            proxies = {'http': proxy.value}
            response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=15)
            if response.status_code == 200:
                # return json.loads(response.text)['origin'] == proxy.value
                return True
        except:
            pass
        return False

def exam_run():
    queue = Queue(settings.QUEUE_SIZE)
    master = MasterThread(queue)
    master.start()

    for i in range(settings.EXAM_SIZE):
        slave = SlaveThread(queue, master)
        slave.daemon = True
        slave.start()

