Tutorial
========

Basic Usage
-----------

You need to know two things to create a `LazyFile`. The length
of the file, and how to get a block of data from it.

```python3
>>> from lazyfile import LazyFile
>>> lf = LazyFile(size, reader)
```

The size is just an integer. The `reader` argument is a function
which will be passed the range of bytes to read, expressed as the
index of the start of the range, and the index one past the end of
the range (this is the same convention as for Python ranges). The
indices will always be between 0 and the size of the file.

As a simple example, the following will implement a reader for a
byte string:

```python3
>>> data = b"Hello, world!"
>>> def get_bytes(lo, hi):
...     return data[lo:hi]
...
>>> lf = LazyFile(len(data), get_bytes)
>>> lf.seek(3)
3
>>> lf.read(4)
b'lo, '
```

Obviously, this is pointless, as `io.BytesIO` does the job far more
effectively. The `LazyFile` class is intended for use when the
`get_bytes` function is expensive, and it is worth minimising the
number of calls to it. But the above is fully functional, and
demonstrates the usage without needing a more complex data source.
