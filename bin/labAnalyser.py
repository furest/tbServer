from scapy.all import *
#from config import *
from includes.config import *
from threading import Thread, Lock, Timer
import mysql.connector
class LabAnalyzer(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.table_columns = dict()
        self.mutex = Lock()
        self._timer = None
        self.commit_interval = config['COMMIT_INTERVAL']
        self.packets = dict()


    def run(self):
        self.launch_commit_timer()
        sockUDP = conf.L2listen(type=ETH_P_IP, iface='tunUDP', filter="udp dst port 4789 and dst host 172.16.100.1")
        sockTCP = conf.L2listen(type=ETH_P_IP, iface='tunTCP', filter="udp dst port 4789 and dst host 172.16.100.129")
        sniff(store=False,opened_socket=[sockUDP, sockTCP],prn=self.analyze_packet)

    def commit(self):
        db = mysql.connector.connect(**tbParams)
        c = db.cursor(dictionary=True)
        self.mutex.acquire()
        local_packets = self.packets
        self.packets = dict()
        self.mutex.release()
        for src_ip, sent_packets in local_packets.items():
            req = """UPDATE laborations_statistics 
                      SET nb_packets = nb_packets + %s
                      WHERE lab_id = (SELECT laborations.ID FROM laborations 
                                       INNER JOIN connected_clients c1 on c1.ID = laborations.init_academy
                                       INNER JOIN connected_clients c2 on c2.ID = laborations.invited_academy
                                       WHERE c1.virt_ip IS NOT NULL 
                                       AND c2.virt_ip IS NOT NULL 
                                       AND (c1.virt_ip = %s 
                                       OR c2.virt_ip = %s)
                                       GROUP BY laborations.ID, laborations.started_at
                                       HAVING laborations.started_at = max(laborations.started_at)
                                      )"""
            req_tuple = (sent_packets, src_ip, src_ip)
            c.execute(req, req_tuple)
        db.commit()
        self.launch_commit_timer()

    def launch_commit_timer(self):
        self._timer = Timer(self.commit_interval, self.commit)
        self._timer.start()


    def analyze_packet(self, packet):
        src_ip = packet[0].src
        self.mutex.acquire()
        self.packets[src_ip] = self.packets.get(src_ip, 0) + 1
        self.mutex.release()



if __name__ == "__main__":
    la = LabAnalyzer()
    la.start()

