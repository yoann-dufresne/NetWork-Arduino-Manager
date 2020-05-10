import argparse
import signal

from manager.registry import Registry
from manager.arduinomanager import ArduinoManager
from connectors.WebServer import WebServer


def parse_arguments():
    parser = argparse.ArgumentParser(description='Deploy an arduino manager and registry over the network.')
    parser.add_argument('--sketch_directory', '-s', default='sketches', help='Define the directory to look at for arduino programs.')
    parser.add_argument('--registry', '-r', default='registry.tsv', help='The file where the arduino registry is saved.')
    parser.add_argument('--web_port', '-w', type=int, default=8080, help="Output file prefix.")

    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()

    # Load the registry
    reg = Registry(sketches_path=args.sketch_directory, registry_file=args.registry)
    manager = ArduinoManager()
    manager.add_listener(reg.manager_listener)
    serv = WebServer(reg, port=args.web_port)
    serv.start()

    def signal_handler(sig, frame):
        print()
        serv.stop()
        manager.stop()
    signal.signal(signal.SIGINT, signal_handler)

    serv.join()
    manager.join()


if __name__ == "__main__":
    main()
