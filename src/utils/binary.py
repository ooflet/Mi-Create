from mmap import mmap, ACCESS_READ

class WatchfaceBinary:
    def __init__(self, path):
        with open(path, "+rb") as binary:
            self.binary = mmap(binary.fileno(), 0)

    def setId(self, id):
        if len(id) == 9:
            self.binary[40:49] = bytes(id, encoding='ascii')
            self.binary.flush()
        else:
            raise ValueError("ID must be 9 numbers long!")