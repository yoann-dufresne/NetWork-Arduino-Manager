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

        self.known_boards = {}  # Board: sketch name
        self.sketches = {}
        self.revert_sketches = {}
        self.load_sketch_list()
        self.load()

    def add_board(self, board):
        if board not in self.known_boards:
            self.known_boards[board] = None
        else:
            sketch_name = self.known_boards[board]
            del self.known_boards[board]
            self.known_boards[board] = sketch_name

        self.save()

    def link_sketch(self, board, sketch):
        if not board in self.known_boards:
            self.add_board(board)

        if not sketch in self.sketches:
            print(f"Unknown sketch: Impossible to link {sketch}. Sketch not present in {self.sketches_path}", file=sys.stderr)
            return

        self.known_boards[board] = sketch
        self.save()

    def load_sketch_list(self):
        for root, dirs, files in os.walk(self.sketches_path):
            for file in files:
                if(file.endswith(".ino")):
                    self.sketches[str(file)] = str(root)
                    self.revert_sketches[str(root)] = str(file)

    def manager_listener(self, event, args):
        if event == "add":
            self.add_board(args)
        elif event == "upload":
            board, sketch = args
            sketch = self.revert_sketches[sketch]
            self.link_sketch(board, sketch)

    def save(self):
        with open(self.registry_file, "w") as registry:
            for board, sketch_name in self.known_boards.items():
                print(f"{board}\t{sketch_name}", file=registry)

    def load(self):
        if os.path.isfile(self.registry_file):
            with open(self.registry_file) as registry:
                for line in registry:
                    board_details, sketch_name = line.strip().split("\t")
                    name, serial = board_details[:-1].split(' (')
                    board = Board(board=name, serial=serial)
                    self.known_boards[board] = sketch_name
