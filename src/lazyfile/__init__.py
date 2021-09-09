import io
from .sparsebytes import SparseBytes


class LazyFile(io.RawIOBase):
    def __init__(self, size, getter):
        self.pos = 0
        self.end = size
        self.buffer = SparseBytes(size, getter)
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
        return self.buffer[start:end]
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

if __name__ == "__main__":  # pragma: no cover
    data = b"Hello,\nworld"
    def getter(start, end):
        return data[start:end]
    f = LazyFile(len(data), getter)
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
