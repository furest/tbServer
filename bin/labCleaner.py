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
            exist_for = now - lab['started_at']
            if (lab['prolongated'] == False and exist_for.seconds >= config['MAX_LAB_TIME']) or (lab['prolongated'] == True and exist_for.seconds >= config['MAX_PROLONGATED_LAB_TIME']):
                lab_stats = tb.get_lab_stats(lab_id=lab['ID'])
                no_packets_for = now - lab_stats[0]['last_packet']
                print("lab " + str(lab['ID']) + " has had no packet for " + str(no_packets_for.seconds))
                if lab['prolongated'] == False and no_packets_for.seconds < config['LAST_PACKET_MIN_WAIT']:
                    tb.update_labs(ID=lab['ID'], prolongated=True)
                else:
                    tb.update_labs(lab['ID'], over=True)
                    client = tb.get_connected_client(ID=lab['init_academy'])
                    if len(client) != 0:
                        delete_association(client[0]['virt_ip'])
                    else:
                        client = tb.get_connected_client(ID=lab['invited_academy'])
                        if len(client) != 0:
                            delete_association(client[0]['virt_ip'])

if __name__ == "__main__":
    lc = LabCleaner()
    lc.start()

