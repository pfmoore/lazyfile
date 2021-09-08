import io
from .sparsebytes import SparseBytes


class LazyFile(io.RawIOBase):
    def __init__(self):
        self.pos = 0
        # Cache this as it may be costly to compute
        self.end = self.get_size()
    def get_size(self):
        # Subclasses implement this
        raise NotImplemented
    def get_data(self, start, end):
        # Subclasses implement this
        # Start and end are guaranteed in range
        raise NotImplemented
    def clamp(self, target):
        if target < 0:
            return 0
        if target > self.end:
            return self.end
        return target
    def readable(self):
        # Defaults to False
        return True
    def seekable(self):
        # Defaults to False
        return True
    def read(self, size=-1):
        if size == -1:
            end = self.end
        else:
            end = self.clamp(self.pos + size)
        start = self.pos
        self.pos = end
        return self.get_data(start, end)
    def seek(self, offset, whence=io.SEEK_SET):
        if whence == io.SEEK_SET:
            target = offset
        elif whence == io.SEEK_CUR:
            target = self.pos + offset
        elif whence == io.SEEK_END:
            target = self.end + offset
        self.pos = self.clamp(target)
        return self.pos
    def tell(self):
        # Not necessary, default uses seek()
        return self.pos

class LazyBufferedFile(LazyFile):
    def __init__(self, size, getter):
        self.size = size
        self.buffer = SparseBytes(size, getter)
        super().__init__()
    def get_size(self):
        return self.size
    def get_data(self, start, end):
        return self.buffer[start:end]


class MyLazyFile(LazyFile):
    def __init__(self, data):
        self.data = data
        super().__init__()
    def get_size(self):
        return len(self.data)
    def get_data(self, start, end):
        return self.data[start:end]

if __name__ == "__main__":
    f = MyLazyFile(b"Hello,\nworld")
    print(f.readall())
    #print(f.fileno()) UnsupportedOperation
    print("Isatty:", f.isatty())
    print("Seekable:", f.seekable())
    print("Readable:", f.readable())
    print("Writable:", f.writable())
    f.seek(0)
    print(list(f.readlines()))
    print(f.tell())
    #f.truncate()
    #f.writelines(["a"])
    f.flush()
    print("Closed:", f.closed)
    f.close()
    print("Closed (after close():", f.closed)
