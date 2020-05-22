import argparse
import signal

from manager.registry import Registry
from manager.arduinomanager import ArduinoManager
from connectors.WebServer import WebServer
from connectors.P2PServer import P2PServer


def parse_arguments():
    parser = argparse.ArgumentParser(description='Deploy an arduino manager and registry over the network.')
    parser.add_argument('--sketch_directory', '-s', default='sketches', help='Define the directory to look at for arduino programs.')
    parser.add_argument('--registry', '-r', default='registry.tsv', help='The file where the arduino registry is saved.')
    parser.add_argument('--web_port', '-w', type=int, default=8080, help="Output file prefix.")
    parser.add_argument('--no_webserver', '-nw', action="store_true")

    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()

    # Load the registry
    reg = Registry(sketches_path=args.sketch_directory, registry_file=args.registry)
    manager = ArduinoManager()
    manager.add_listener(reg.manager_listener)
    if not args.no_webserver:
        webserv = WebServer(reg, manager, port=args.web_port)
        webserv.start()
    p2pserv = P2PServer(reg, manager)
    p2pserv.start()


    def signal_handler(sig, frame):
        print()
        if not args.no_webserver:
            webserv.stop()
        p2pserv.stop()
        manager.stop()
    signal.signal(signal.SIGINT, signal_handler)

    if not args.no_webserver:
        webserv.join()
    p2pserv.join()
    manager.join()


if __name__ == "__main__":
    main()
