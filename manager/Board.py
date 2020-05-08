from serial.tools import list_ports

class Board:

    def __init__(self, port=None, type=None, board=None, core=None, serial=None):
        self.port = port
        self.type = type
        self.board = board
        self.core = core
        self.serial = serial

    def get_serial(self):
        port_details = list(list_ports.grep(self.port))[0]
        self.serial = port_details.serial_number

    def __repr__(self):
        return f"{self.board} ({self.serial})"

    def __hash__(self):
        return self.serial.__hash__()

    def __eq__(self, other):
        if isinstance(other, Board):
            return self.serial == other.serial
        else:
            return False
