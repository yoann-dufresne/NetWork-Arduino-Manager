from threading import Thread
import sys
import random
import string

import zmq
import time


class P2PServer(Thread):

    def __init__(self, registery, manager, p2p_start_ip="192.168.1.40", port=8484):
        Thread.__init__(self)

        self.uniq_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))

        self.registery = registery
        self.manager = manager

        self.context = zmq.Context()
        self.bcast = self.context.socket(zmq.PUB)
        try:
            self.bcast.bind(f"tcp://*:{port}")
            self.stopped = False
        except zmq.error.ZMQError:
            print(f"Port {port} already in use. P2P server stopped")
            self.stopped = True
        
        self.p2p_start_ip = p2p_start_ip.split('.')
        self.port = port


    def run(self):
        if self.stopped:
            return
            
        listener = self.context.socket(zmq.SUB)

        base_ip = '.'.join(self.p2p_start_ip[:-1])
        last_ip_num = int(self.p2p_start_ip[-1])
        for offset in range(10):
            listener.connect(f"tcp://{base_ip}.{str(last_ip_num + offset)}:{self.port}")

        listener.setsockopt(zmq.SUBSCRIBE, b'')
        print(f"Peer to peer server launched on port {self.port}")
        while not self.stopped:
            try:
                print(listener.recv_string())
            except (KeyboardInterrupt, zmq.ContextTerminated):
                break

        print("Peer to peer closed")

    def stop(self):
        self.stopped = True
        self.bcast.close()
        self.context.destroy()

    def send_message(self, msg):
        if not self.stopped:
            self.bcast.send_string(msg)
