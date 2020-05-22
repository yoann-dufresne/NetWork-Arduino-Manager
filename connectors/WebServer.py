import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import os


class WebServer(threading.Thread):

    def __init__(self, registry, manager, port=80):
        threading.Thread.__init__(self)
        self.port = port
        self.stopped = False
        self.registry = registry
        self.manager = manager

    def run(self):
        # Create the HTTP server
        path = '/'.join(__file__.split('/')[:-2])
        self.server = MyHTTPServer(self.port, f"{path}/www")
        registry = self.registry

        # Declare the services
        def list_sketches(path):
            content = ",".join(registry.sketches.keys())
            return "text/plain", content.encode("utf-8")
        self.server.declare_service("/sketches", list_sketches)
        def list_arduinos(path):
            content = "\n".join([f"{board.tsv_string()}\t{sketch}" for board, sketch in registry.known_boards.items()])
            return "text/plain", content.encode("utf-8")
        self.server.declare_service("/arduinos", list_arduinos)
        self.server.declare_service("/upload", self.upload_sketch)

        # Serve forever
        print("webserver initiated at port", self.port)
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()
        self.stopped = True
        print("HTTP server stopped")

    # Define some services
    def upload_sketch(self, path):
        # Parse args
        sp = path.split("/")
        serial = sp[-2]
        sketch = sp[-1]

        # Sanity chcks
        if serial not in self.registry.board_per_serial:
            return "text/plain", b"ko: Wrong serial number"
        board = self.registry.board_per_serial[serial]
        if sketch not in self.registry.sketches:
            return "text/plain", b"ko: Wrong sketch name"
        sketch = self.registry.sketches[sketch]
        
        # upload
        self.manager.upload_sketch(board, sketch)
        return "text/plain", b"ok"


class MyHTTPServer(HTTPServer):

    def __init__(self, port=80, served_directory="www"):
        HTTPServer.__init__(self, ('', port), HandleRequest)
        self.port = port
        self.served_path = os.path.abspath(served_directory)
        self.services = {}

    def declare_service(self, name, handler):
        self.services[name] = handler

    def is_valid_file(self, file):
        path = str(os.path.abspath(os.path.join(self.served_path, file)))
        # Verify a subdirectory search
        if not path.startswith(str(self.served_path)):
            return False

        # Verify file existance
        return os.path.isfile(path)

    def get_file_content(self, file):
        path = str(os.path.abspath(os.path.join(self.served_path, file)))
        content_type = None
        extention = path.split(".")[-1].lower()

        if extention == "html":
            content_type = "text/html"
        elif extention == "css":
            content_type = "text/css"
        elif extention == "png":
            content_type = "image/png"
        elif extention == "jpeg":
            content_type = "image/jpeg"
        else:
            content_type = "text/plain"

        content = None
        with open(path, 'r+b') as f:
            content = f.read()

        return content_type, content


class HandleRequest(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/":
            self.path = "/index.html"

        self.path_root = '/'.join(self.path.split('/')[:2])

        filepath = self.path[1:]
        if self.server.is_valid_file(filepath):
            type, content = self.server.get_file_content(filepath)
            self.send_response(200)
            self.send_header("Content-type", type)
            self.end_headers()
            self.wfile.write(content)
        elif self.path_root in self.server.services:
            self.send_response(200)
            type, content = self.server.services[self.path_root](self.path)
            self.send_header("Content-type", type)
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_response(404)

