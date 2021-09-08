from lazyfile import LazyBufferedFile

def test_simple():
    data = b'Hello, world!'
    def get_data(lo, hi):
        return data[lo:hi]
    with LazyBufferedFile(len(data), get_data) as f:
        assert f.read() == data
