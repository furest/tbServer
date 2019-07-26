from threading import Timer
import datetime

from includes.config import *
import includes.twinbridge_access as tb
from includes.makeAssociation import *
class LabCleaner(object):
    def __init__(self):
        self.timer      = None
        self.interval   = config['CLEAN_INTERVAL']
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.cleanLabs()

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False
    
    def cleanLabs(self):
        labs = tb.get_lab(over=False)
        for lab in labs:
            now = datetime.datetime.now()
            diff = now - lab['started_at']
            if diff.seconds >= config['MAX_LAB_TIME']:
                tb.update_labs(lab['ID'], over=True)
                client = tb.get_connected_client(ID=lab['init_academy'])
                if len(client) != 0:
                    delete_association(client[0]['virt_ip'])
                else:
                    client = tb.get_connected_client(ID=lab['invited_academy'])
                    if len(client) != 0:
                        delete_association(client[0]['virt_ip'])



