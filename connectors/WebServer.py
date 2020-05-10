import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import os


class WebServer(threading.Thread):

    def __init__(self, registry, port=80):
        threading.Thread.__init__(self)
        self.port = port
        self.stopped = False

    def run(self):
        path = '/'.join(__file__.split('/')[:-2])
        self.server = MyHTTPServer(self.port, f"{path}/www")
        print("webserver initiated at port", self.port)
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()
        self.stopped = True
        print("HTTP server stopped")


class MyHTTPServer(HTTPServer):

    def __init__(self, port=80, served_directory="www"):
        HTTPServer.__init__(self, ('', port), HandleRequest)
        self.port = port
        self.served_path = os.path.abspath(served_directory)

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

        filepath = self.path[1:]
        if self.server.is_valid_file(filepath):
            type, content = self.server.get_file_content(filepath)
            self.send_response(200)
            self.send_header("Content-type", type)
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_response(404)

