import os
import sys

from manager.Board import Board


default_path = os.path.dirname(os.path.abspath(__file__))
default_path = '/'.join(str(default_path).split('/')[:-1])
default_sketches_path = default_path + "/sketches"
default_registry_file = default_path + "/registry.tsv"


class Registry:

    def __init__(self, sketches_path=default_sketches_path, registry_file=default_registry_file):
        self.sketches_path = sketches_path
        self.registry_file = registry_file

        self.board_per_serial = {}
        self.board_sketch_links = {}  # Board: sketch name
        self.sketches = {}
        # self.revert_sketches = {}
        if sketches_path is not None and registry_file is not None:
            self.load_sketch_list()
            self.load()

    def add_board(self, board):
        if board not in self.board_sketch_links:
            self.board_sketch_links[board] = None
        else:
            sketch_name = self.board_sketch_links[board]
            del self.board_sketch_links[board]
            self.board_sketch_links[board] = sketch_name

        self.board_per_serial[board.serial] = board

        self.save()

    def link_sketch(self, board, sketch):
        if not board in self.board_sketch_links:
            self.add_board(board)

        if not sketch.name in self.sketches:
            print(f"Unknown sketch: Impossible to link {sketch.name}. Sketch not present in {self.sketches_path}", file=sys.stderr)
            return

        self.board_sketch_links[board] = sketch.name
        self.save()

    def load_sketch_list(self):
        for root, dirs, files in os.walk(self.sketches_path):
            for file in files:
                if file.endswith(".ino"):
                    path = os.path.join(root, file)
                    time = os.path.getmtime(path)
                    sk = Sketch(file, root_dir=root, last_modif=time)
                    self.sketches[str(file)] = sk
                    # self.revert_sketches[str(root)] = str(file)

    def manager_listener(self, event, args):
        if event == "add":
            self.add_board(args)
        elif event == "upload":
            board, sketch_dir = args
            sketch_name = sketch_dir.split("/")[-1] + ".ino"
            sketch = self.sketches[sketch_name]
            self.link_sketch(board, sketch)
        elif event == "disconnected":
            board = self.board_per_serial[args.serial]
            board.port = None
            board.connected = False

    def save(self):
        if self.registry_file is not None:
            with open(self.registry_file, "w") as registry:
                for board, sketch_name in self.board_sketch_links.items():
                    print(f"{board}\t{sketch_name}", file=registry)

    def load(self):
        if os.path.isfile(self.registry_file):
            with open(self.registry_file) as registry:
                for line in registry:
                    board_details, sketch_name = line.strip().split("\t")
                    name, serial = board_details[:-1].split(' (')
                    board = Board(board=name, serial=serial)
                    self.board_sketch_links[board] = sketch_name


class Sketch:

    def __init__(self, name, root_dir=None, last_modif=0.):
        self.name = name
        if root_dir is None:
            dir_name = '.'.join(name.split(".")[-1])
            self.dir = f"./sketches/{dir_name}"
        else:
            self.dir = root_dir
        self.last_modif = last_modif

    def hex_filename(self, fqbn):
        trunk = '.'.join(self.name.split('.')[-1])
        endfile = '.'.join(fqbn.split(':')) + ".hex"
        return trunk + "." + endfile

    def save_hex(self, fqbn, bin):
        if not os.path.isdir(self.dir):
            os.mkdir(self.dir)
        with open(self.dir + self.hex_filename(fqbn), "wb") as f:
            ba = bytearray(bin)
            f.write(ba)

    def __hash__(self):
        return self.name.__hash__()
