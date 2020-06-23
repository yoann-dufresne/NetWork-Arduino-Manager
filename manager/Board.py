from serial.tools import list_ports

class Board:

    def __init__(self, port=None, type=None, board=None, fqbn=None, core=None, serial=None, connected=False):
        self.port = port
        self.type = type
        self.board = board
        self.fqbn = fqbn
        self.core = core
        self.serial = serial
        self.connected = connected

    def get_serial(self):
        port_details = list(list_ports.grep(self.port))[0]
        self.serial = port_details.serial_number

    def tsv_string(self):
        return f"{self.port}\t{self.board}\t{self.serial}"

    def __repr__(self):
        return f"{self.board} ({self.serial})"

    def __hash__(self):
        return self.serial.__hash__()

    def __eq__(self, other):
        if isinstance(other, Board):
            return self.serial == other.serial
        else:
            return False
