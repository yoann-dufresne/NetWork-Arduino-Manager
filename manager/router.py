

class ArduinoRouter:

    def __init__(self, registry, manager):
        self.registry = registry
        self.manager = manager

    def upload(self, serial, sketch_name):
        # Sanity checks
        if serial not in self.registry.board_per_serial:
            raise KeyError("ko: Wrong serial number")
        board = self.registry.board_per_serial[serial]
        if sketch_name not in self.registry.sketches:
            raise KeyError("ko: Wrong sketch name")
        sketch = self.registry.sketches[sketch_name]
        
        # upload
        self.manager.place_upload_sketch(board, sketch.dir)
        return True

    def list_sketches(self):
        return list(self.registry.sketches.keys())

    def list_board_sketch_pairs(self):
        return list(self.registry.board_sketch_links.items())
