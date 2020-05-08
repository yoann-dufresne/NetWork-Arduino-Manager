import manager.arduinocliwrapper as wrap
from manager.registry import Registry
from manager.arduinomanager import ArduinoManager


def main():
    reg = Registry()
    manager = ArduinoManager()
    manager.add_listener(reg.manager_listener)
    manager.discover_boards()


if __name__ == "__main__":
    main()
    