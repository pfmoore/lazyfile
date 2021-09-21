LazyFile How To Guides
======================

How to lazily extract a file from a remote wheel
------------------------------------------------

The original motivation for this library was to extract the
metadata file from a wheel, without downloading the whole
wheel file (which could potentially be very large).

Wheel files are structured as zip files, and can be read using
the standard library `zipfile` module. The `ZipFile` constructor
takes a file-like object which must return bytes, and be seekable.
A LazyFile is ideal for this.

First, we need to implement methods to get the length of the file,
and to get a block of bytes from the file.

```python3
from urllib.request import Request, urlopen

# Get the file size with a HEAD request
def content_len(url):
    req = Request(url, method="HEAD")
    with urlopen(req) as f:
        return int(f.headers["Content-Length"])

# Get a block of bytes from the URL.
def get_url_range(url, lo, hi):
    # Adjust the range, as hi is "past the end"
    req = Request(url, headers={"Range": f"bytes={lo}-{hi-1}"})
    with urlopen(req) as f:
        data = f.read()
        if len(data) != hi-lo:
            raise ValueError(f"Failed to read {hi-lo} bytes")

    return data
```

With these helpers, we can open a URL lazily

```python3
from lazyfile import LazyFile
from functools import partial

def open_url(url):
    url_getter = partial(get_url_range, url)
    file_size = content_len(url)
    return LazyFile(file_size, url_getter)
```

And that's all we need to process the file as a zipfile and
extract the metadata

```python3
def extract_metadata(url)
    f = open_url(url)
    z = ZipFile(f)
    for name in z.namelist():
        if name.endswith(".dist-info/METADATA"):
            metadata = z.read(name)
            return metadata
```