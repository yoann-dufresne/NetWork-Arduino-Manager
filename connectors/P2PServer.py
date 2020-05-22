from threading import Thread
import socketserver
import sys


class MyTCPHandler(socketserver.BaseRequestHandler):

    p2p = None

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.text = self.request.recv(1024).strip().encode('utf-8')
        ip = self.client_address[0]
        # just send back the same data, but upper-cased
        self.request.sendall(b"pouet")


class P2PServer(Thread):

    def __init__(self, registery, manager, port=8484):
        Thread.__init__(self)

        self.registery = registery
        self.manager = manager

        self.port = port
        self.server = None
        self.sockets = {}
        self.stopped = False

    def run(self):
        MyTCPHandler.p2p = self

        for port_index in range(self.port, self.port + 100):
            try:
                # Create the server, binding to localhost on port 9999
                with socketserver.TCPServer(("localhost", port_index), MyTCPHandler) as server:
                    self.port = port_index
                    print(f"Server socket started on port {self.port}")
                    self.server = server
                    # Activate the server; this will keep running until you
                    # interrupt the program with Ctrl-C
                    self.server.serve_forever()
            except OSError:
                continue
            if self.stopped:
                break

        if not self.stopped:
            print("Impossible to create a server socket", file=sys.stderr)

    def stop(self):
        self.stopped = True
        self.server.shutdown()
