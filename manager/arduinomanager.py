import time
import os
from threading import Thread

import manager.arduinocliwrapper as wrap
from manager.Board import Board


class ArduinoManager(Thread):

    def __init__(self):
        Thread.__init__(self)

        self.boards = set()
        self.listeners = set()
        self.cores = {}
        self.update_installed_cores()

        self.to_upload = []

        self.stopped=False
        self.start()

    def run(self):
        while not self.stopped:
            # Board discovery
            self.discover_boards()
            # Sketch uploads
            postponed = []
            # Trigger compilations
            while len(self.to_upload) > 0:
                sketch, board, compile, upload = self.to_upload.pop()
                if compile and upload:
                    self._real_compile_upload(board, sketch)
                elif compile:
                    self._real_compile(board, sketch)
                elif upload: 
                    if not self._real_upload(board, sketch):
                        postponed.append((sketch, board, compile, upload))

            # Trigger distant upload
            # TODO

            self.to_upload = postponed
            # Regularity trigger
            time.sleep(1)

    def stop(self):
        self.stopped = True

    def update_installed_cores(self):
        core_names = [core["ID"] for core in wrap.core_list()]
        self.cores = frozenset(core_names)

    def discover_boards(self):
        boards_generals_list = wrap.board_list()
        prev_boards = set(self.boards)

        for boards_generals in boards_generals_list:
            board = Board(
                port=boards_generals["Port"],
                type=boards_generals["Type"],
                board=boards_generals["Board Name"],
                fqbn=boards_generals["FQBN"],
                core=boards_generals["Core"],
                connected=True
            )
            board.get_serial()
            if board in prev_boards:
                prev_boards.remove(board)

            # Install the core if not already present
            if board.core not in self.cores:
                wrap.core_install(board.core)
                self.update_installed_cores()

            if not board in self.boards:
                self.boards.add(board)
                self.notify("add", board)
        
        # Update status for board disconnected
        for board in prev_boards:
            self.boards.remove(board)
            self.notify("disconnected", board)

    def place_upload_sketch(self, board, sketch, compile=True, upload=True):
        self.to_upload.append((board, sketch, compile, upload))

    def _real_compile(self, board, sketch):
        if wrap.compile(board.fqbn, sketch.dir):
            self.notify("compiled", [sketch, board])

    def _real_upload(self, board, sketch):
        hex_file = sketch.dir.split('/')[-1]
        hex_file += '.'.join(board.fqbn.split(':')) + ".hex"
        if not os.path.isfile(f"{sketch.dir}/{hex_file}"):
            print(hex_file, "not a file")
            return False

        if wrap.upload(board.port, board.fqbn, sketch.dir):
            self.notify("upload", [board, sketch.dir])
            return True
        return False

    def _real_compile_upload(self, board, sketch):
        if wrap.compile(board.fqbn, sketch.dir) and wrap.upload(board.port, board.fqbn, sketch.dir):
            self.notify("upload", [board, sketch.dir])


    def add_listener(self, listener):
        self.listeners.add(listener)

    def notify(self, event, args):
        for listener in self.listeners:
            listener(event, args)

