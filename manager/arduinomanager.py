import manager.arduinocliwrapper as wrap
from manager.Board import Board


class ArduinoManager:

    def __init__(self):
        self.boards = set()
        self.listeners = set()

    def discover_boards(self):
        print("discover")
        boards_generals_list = wrap.board_list()

        for boards_generals in boards_generals_list:
            board = Board(
                port=boards_generals["Port"],
                type=boards_generals["Type"],
                board=boards_generals["Board Name"],
                core=boards_generals["Core"]
            )
            board.get_serial()

            if not board in self.boards:
                self.boards.add(board)
                self.notify_add(board)

    def add_listener(self, listener):
        self.listeners.add(listener)

    def notify_add(self, board):
        for listener in self.listeners:
            listener("add", board)

