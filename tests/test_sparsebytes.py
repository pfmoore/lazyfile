from lazyfile.sparsebytes import SparseBytes
from spans import intrange, intrangeset
import pytest

def test_simple():
    data = b'Hello, world!'
    def get_data(lo, hi):
        return data[lo:hi]
    sb = SparseBytes(len(data), get_data)
    ranges = [(1,1), (3,6), (-5,-1), (-1,None)]
    for lo, hi in ranges:
        b = sb[lo:hi]
        assert b == data[lo:hi]

def test_length():
    data = b'Hello, world!'
    def get_data(lo, hi):
        return data[lo:hi]
    sb = SparseBytes(len(data), get_data)
    assert len(sb) == len(data)

def test_read_byte():
    data = b'Hello, world!'
    def get_data(lo, hi):
        return data[lo:hi]
    sb = SparseBytes(len(data), get_data)
    for i in range(len(data)):
        assert sb[i] == data[i]
        assert sb[-i] == data[-i]

def test_index_error():
    data = b'Hello, world!'
    def get_data(lo, hi):
        return data[lo:hi]
    sb = SparseBytes(len(data), get_data)
    with pytest.raises(IndexError):
        _ = sb[99]
        # Not clear why this doesn't end up with a block (99, 100, b'')
        assert not sb.blocks

def test_coalesce():
    data = b'Hello, world!'
    def get_data(lo, hi):
        return data[lo:hi]
    sb = SparseBytes(len(data), get_data)
    sb._coalesce()
    assert len(sb.blocks) == 0
