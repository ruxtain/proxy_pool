"""
    Check the functionality of a proxy
"""

from proxy_pool import db
from proxy_pool import settings
from proxy_pool.db import Proxy
from proxy_pool.utils import print_log

from datetime import datetime
from queue import Queue
import threading
import requests
import time

class MasterThread(threading.Thread):
    """ Get proxy from mongodb to exam """

    def __init__(self, queue):
        self.queue = queue
        super().__init__()

    def run(self):
        """ sort by count (descending) then by update_time (ascending)
        so it removes bad ones more efficiently
        """
        while True:
            for proxy in Proxy.aggregate([{ "$sort" : { "count": -1, "update_time": 1 } }]):
                self.queue.put(proxy)

class SlaveThread(threading.Thread):
    """ Check if the proxy works """

    def __init__(self, queue):
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
            response = requests.get(
                    settings.EXAM_WEBSITE,
                    proxies=proxies,
                    timeout=8,
                    allow_redirects=False
                )
            if response.status_code == 200:
                return True
            elif response.status_code == 502:
                return False
        except Exception as e:
            e = str(e)
            if 'Connection refused' in e:
                print_log('Connection refused {}'.format(proxy.value))
            elif 'connect timeout=' in e or 'Read timed out.' in e:
                print_log('Connection timeout {}'.format(proxy.value))
            else:
                print_log(e)
        return False

def exam_run():
    """SlaveThread must start first or the Master's queue.put will block
    """
    queue = Queue(settings.EXAM_QUEUE_SIZE)
    master = MasterThread(queue)
    master.start()

    for i in range(settings.EXAM_WORKERS):
        slave = SlaveThread(queue)
        slave.daemon = True
        slave.start()




