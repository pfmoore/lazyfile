import io

from lazyfile import LazyFile


def test_simple():
    data = b"Hello, world!"

    def get_data(lo, hi):
        return data[lo:hi]

    with LazyFile(len(data), get_data) as f:
        assert f.readable()
        assert f.seekable()
        assert f.tell() == 0
        f.seek(0, io.SEEK_END)
        assert f.tell() == len(data)
        f.seek(5, io.SEEK_SET)
        assert f.tell() == 5
        assert f.read(2) == data[5:7]
        assert f.tell() == 7
        f.seek(-7, io.SEEK_CUR)
        assert f.tell() == 0
        assert f.read() == data


def test_long_read():
    data = b"Hello, world!"

    def get_data(lo, hi):
        return data[lo:hi]

    with LazyFile(len(data), get_data) as f:
        assert f.read(1000) == data


def test_out_of_range():
    data = b"Hello, world!"

    def get_data(lo, hi):
        return data[lo:hi]

    with LazyFile(len(data), get_data) as f:
        f.seek(1000)
        assert f.tell() == len(data)
        f.seek(-1000)
        assert f.tell() == 0
