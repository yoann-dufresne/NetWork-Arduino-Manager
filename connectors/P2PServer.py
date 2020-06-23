import os
import sys
from threading import Thread
import random
import string

import zmq

from manager.Board import Board
from manager.router import ArduinoRouter
from manager.registry import Registry, Sketch


class P2PServer(Thread):

    def __init__(self, registry, manager, p2p_start_ip="192.168.1.40", port=8484):
        Thread.__init__(self)

        self.uniq_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))

        self.registry = registry
        self.manager = manager
        self.distant_registry = Registry(None, None)
        self.router = P2PRouter(self)

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
        self.known_host = set()

        self.manager.add_listener(self.handle_local_changes)


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
                self.handle_msg(listener.recv_string(), listener)
            except (KeyboardInterrupt, zmq.ContextTerminated):
                break

        print("Peer to peer closed")

    def stop(self):
        self.stopped = True
        self.bcast.close()
        self.context.destroy()

    def send_message(self, msg):
        if not self.stopped:
            self.bcast.send_string(f"{self.uniq_id} {msg}")

    def send_and_wait(self, msg):
        if not self.stopped:
            self.bcast.send_string(f"{self.uniq_id} {msg}")
            return self.bcast.recv()
        return b""

    def handle_local_changes(self, event, args):
        if event == "add":
            board = args
            sketch_name = self.registry.board_sketch_links[board]
            self.send_message(f"declare board {board.serial} {sketch_name} {board.fqbn}")
        elif event == "disconnected":
            board = args
            self.send_message(f"retract board {board.serial}")
        elif event == "compiled":
            sketch, board = args
            if sketch.name in self.router.to_distant_upload:
                self.prepare_file_upload()
                self.send_message(f"upload {sketch.name} {board.serial}")


    def handle_msg(self, msg, socket):
        if msg.startswith(self.uniq_id):
            return

        sp = msg.split(' ')[1:]
        msg = ' '.join(sp)
        key = sp[0]

        if key == "declare":
            obj = sp[1]
            if obj == "board":
                self.declare_board(msg)
            elif obj == "sketch":
                self.declare_sketch(msg)

        elif key == "retract":
            if sp[1] == "board":
                self.remove_board(msg)
        elif key == "download":
            self.download_sketch_answer(msg, socket)
        elif key == "upload":
            self.upload_to_board(msg)

    def download_sketch_answer(self, msg, socket):
        sp = msg.split(' ')
        sketch_name = sp[1]

        if sketch_name not in self.registry.sketches:
            return

        sketch = self.registry.sketches[sketch_name]
        filename = str(os.path.join(sketch.dir, sketch.name))

        if len(sp) > 2:
            fqbn = sp[2].replace(':', '.')
            filename = f"{'.'.join(filename.split('.')[:-1])}.{fqbn}.hex"

        socket.send(open(filename, "rb").read())

    def upload_to_board(self, msg):
        sp = msg.split(' ')
        sketch_name = sp[1]
        board_serial = sp[2]

        if board_serial in self.registry.board_per_serial:
            board = self.registry.board_per_serial[board_serial]
            sketch = None
            if sketch_name in self.registry.sketches:
                sketch = self.registry.sketches[sketch_name]
            else:
                # print(self.distant_registry.sketches)
                # sketch = self.distant_registry.sketches[sketch_name]
                # Download sketch if needed
                sketch = Sketch(sketch_name)
                file_content = self.send_and_wait(f"download {sketch_name} {board.fqbn}")
                sketch.save_hex(board.fqbn, file_content)

            if board.connected:
                # Upload the code
                self.manager.place_upload_sketch(sketch, board, upload=True, compile=False)

    def remove_board(self, msg):
        sp = msg.split(' ')
        serial = sp[2]

        if serial in self.distant_registry.board_per_serial:
            self.distant_registry.board_per_serial[serial].connected = False

    def declare_board(self, msg):
        sp = msg.split(' ')
        board_serial = sp[2]
        sketch_name = sp[3]
        fqbn = sp[4]

        # port=None, type=None, board=None, fqbn=None, core=None, serial=None, connected=False
        board = Board(port="distant", serial=board_serial, connected=True, fqbn=fqbn)
        self.distant_registry.add_board(board)

        if sketch_name in self.distant_registry.sketches:
            sketch = self.distant_registry.sketches[sketch_name]
            self.distant_registry.link_sketch(board, sketch)

    def declare_sketch(self, msg):
        sp = msg.split(' ')
        sketch_name = sp[2]
        sketch_update_time = float(sp[3])

        if sketch_name not in self.distant_registry.sketches or self.distant_registry.sketches[sketch_name].last_modif >= sketch_update_time:
            self.distant_registry.sketches[sketch_name] = Sketch(sketch_name, last_modif=sketch_update_time)

    def get_router(self):
        return self.router


class P2PRouter(ArduinoRouter):

    def __init__(self, p2p):
        ArduinoRouter.__init__(self, p2p.registry, p2p.manager)
        self.p2p = p2p
        self.to_distant_upload = set()

    def manager_listener(self, event, args):
        # TODO: What if compilation failed ?
        if event == "compiled":
            sketch = args[0]
            board = args[1]

            if sketch.name in self.to_distant_upload:
                self.p2p.send_message(f"upload {sketch.name} {board.serial}")

    def upload(self, serial, sketch_name):
        # Sketch sanity checks
        local_sketch = False
        sketch = None
        if sketch_name in self.p2p.registry.sketches:
            local_sketch = True
            sketch = self.p2p.registry.sketches[sketch_name]
        elif sketch_name in self.p2p.distant_registry.sketches:
            local_sketch = False
            sketch = self.p2p.distant_registry.sketches[sketch_name]
        else:
            raise KeyError(f"{sketch_name}: not a valid sketch name")

        # board sanity check
        local_board = True
        board = None
        if serial in self.p2p.registry.board_per_serial:
            local_board = True
            board = self.p2p.registry.board_per_serial[serial]
        elif serial in self.p2p.distant_registry.board_per_serial:
            local_board = False
            board = self.p2p.distant_registry.board_per_serial[serial]
        else:
            raise KeyError(f"{serial}: Wrong arduino serial number")

        # Get sketch if not local
        if not local_sketch:
            print("Distant sketch repository not yet implemented", file=sys.stderr)

        # Compile and upload
        if local_board:
            # Upload the code to the board
            self.p2p.manager.place_upload_sketch(sketch, board, upload=True, compile=True)
        else:
            # Prepare upload and compile
            self.to_distant_upload.add(sketch_name)
            self.p2p.manager.place_upload_sketch(sketch, board, upload=False, compile=True)

    def list_sketches(self):
        sketches = set(list(self.p2p.registry.sketches.values()))

        for sketch in self.p2p.distant_registry.sketches.values():
            if sketch not in sketches:
                sketches.add(sketch)

        return sketches

    def list_board_sketch_pairs(self):
        boards = {}
        # Add local boards
        for board in self.p2p.registry.board_per_serial.values():
            boards[board.serial] = (board, self.p2p.registry.board_sketch_links[board])
        # Add remote board
        for board in self.p2p.distant_registry.board_per_serial.values():
            if board.connected:
                boards[board.serial] = (board, self.p2p.distant_registry.board_sketch_links[board])

        pairs = set()
        for pair in boards.values():
            pairs.add(pair)
        return pairs
