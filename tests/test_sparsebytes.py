from lazyfile.sparsebytes import SparseBytes
from spans import intrange, intrangeset

def test_simple():
    data = b'Hello, world!'
    def get_data(lo, hi):
        return data[lo:hi]
    sb = SparseBytes(len(data), get_data)
    ranges = [(1,1), (3,6), (-5,-1), (-1,None)]
    for lo, hi in ranges:
        b = sb[lo:hi]
        assert b == data[lo:hi]
