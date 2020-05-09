import manager.arduinocliwrapper as wrap
from manager.Board import Board


class ArduinoManager:

    def __init__(self):
        self.boards = set()
        self.listeners = set()
        self.cores = {}
        self.update_installed_cores()

    def update_installed_cores(self):
        core_names = [core["ID"] for core in wrap.core_list()]
        self.cores = frozenset(core_names)

    def discover_boards(self):
        boards_generals_list = wrap.board_list()

        for boards_generals in boards_generals_list:
            board = Board(
                port=boards_generals["Port"],
                type=boards_generals["Type"],
                board=boards_generals["Board Name"],
                fqbn=boards_generals["FQBN"],
                core=boards_generals["Core"]
            )
            board.get_serial()

            # Install the core if not already present
            if board.core not in self.cores:
                wrap.core_install(board.core)
                self.update_installed_cores()

            if not board in self.boards:
                self.boards.add(board)
                self.notify("add", board)

    def upload_sketch(self, board, sketch_dir):
        if wrap.compile(board.fqbn, sketch_dir) and wrap.upload(board.port, board.fqbn, sketch_dir):
            self.notify("upload", [board, sketch_dir])
            return True
        return False


    def add_listener(self, listener):
        self.listeners.add(listener)

    def notify(self, event, args):
        for listener in self.listeners:
            listener(event, args)

