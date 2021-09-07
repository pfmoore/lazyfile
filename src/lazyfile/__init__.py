import io
from spans import intrange, intrangeset


# SparseBytes
# ===========
#
# size = N
# blocks = [(lo, hi, bytes), ...]
# filled = intrangeset(intrange(lo, hi) for lo, hi, _ in blocks)
# gaps = intrangeset(intrange(0, N)).difference(filled)
#
# ensure(lo, hi):
#     need = gaps.intersection(intrangeset([intrange(lo, hi)]))
#     for part_lo, part_hi in need:
#         part = get_bytes(part_lo, part_hi)
#         blocks.append((part_lo, part_hi, part))
#     coalesce(blocks)
#
# coalesce(blocks):
#     # Re-sort blocks, merging adjacent chunks
#     blocks.sort()
#     lo, hi, chunk = blocks.pop(0)
#     new_blocks = []
#     while blocks:
#         next_lo, next_hi, next_chunk = blocks.pop(0)
#         if hi == next_lo:
#             # Merge
#             hi = next_hi
#             chunk += next_chunk
#         else:
#             new_blocks.append((lo, hi, chunk))
#             lo, hi, chunk = next_lo, next_hi, next_chunk
#     new_blocks.append((lo, hi, chunk))
#     return new_blocks



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
        self.getter = getter
        self.blocks = {}
        super().__init__()
    def get_size(self):
        return self.size
    def ensure(self, start, end):
        cached = intrangeset(intrange(start, end) for start, end in self.blocks)
        if intrange(start, end) in cached:
            return
        for range in intrangeset([intrange(start, end)]).difference(cached):
            lo = range.lower
            hi = range.upper
            block = self.getter(lo, hi)
            self.blocks[(lo, hi)] = block
    def get_data(self, start, end):
        self.ensure(start, end)
        for lo, hi in sorted(self.blocks):
            if intrange(start, end):
                pass



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
