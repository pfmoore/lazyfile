from .lazyfile import LazyFile
from .sparsebytes import SparseBytes

if __name__ == "__main__":  # pragma: no cover
    data = b"Hello,\nworld"

    def getter(start, end):
        return data[start:end]

    f = LazyFile(len(data), getter)
    print(f.readall())
    # print(f.fileno()) UnsupportedOperation
    print("Isatty:", f.isatty())
    print("Seekable:", f.seekable())
    print("Readable:", f.readable())
    print("Writable:", f.writable())
    f.seek(0)
    print(list(f.readlines()))
    print(f.tell())
    # f.truncate()
    # f.writelines(["a"])
    f.flush()
    print("Closed:", f.closed)
    f.close()
    print("Closed (after close():", f.closed)
