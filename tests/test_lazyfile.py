from lazyfile import LazyBufferedFile
import io

def test_simple():
    data = b'Hello, world!'
    def get_data(lo, hi):
        return data[lo:hi]
    with LazyBufferedFile(len(data), get_data) as f:
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
