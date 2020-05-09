import manager.arduinocliwrapper as wrap
from manager.registry import Registry
from manager.arduinomanager import ArduinoManager
import time



def main():
    reg = Registry()
    manager = ArduinoManager()
    manager.add_listener(reg.manager_listener)
    manager.discover_boards()

    board = list(manager.boards)[0]
    sketch = reg.sketches["Blink-1s.ino"]
    manager.upload_sketch(board, sketch)
    time.sleep(5)
    sketch = reg.sketches["Blink-01s.ino"]
    manager.upload_sketch(board, sketch)


if __name__ == "__main__":
    main()
