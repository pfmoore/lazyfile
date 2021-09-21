% lazyfile documentation master file, created by
% sphinx-quickstart on Sun Apr 25 10:00:23 2021.
% You can adapt this file completely to your liking, but it should at least
% contain the root `toctree` directive.

# Lazyfile documentation

The `lazyfile` module is an implementation of an "on demand" file object
in Python. It allows you to define how the data for a file is fetched, and
it ensures that as the file is read, data is only requested when needed,
and is cached so that the same block of data is never requested more than
once.

This is useful when requesting data is costly, for example when accessing
a large file over HTTP, where range requests can be used to limit the amount
of network traffic needed.

## Example

We will demonstrate the library by implementing a HTTP-based file, that only
requests data from the server as needed.

```python3
from lazyfile import LazyFile
from urllib.request import Request, urlopen
from functools import partial

# We need to know the size of the file when we
# create the LazyFile object, so we issue a
# HTTP HEAD request to get it
def content_len(url):
    req = Request(url, method="HEAD")
    with urlopen(req) as f:
        return int(f.headers["Content-Length"])

# Get a block of bytes from the URL.
def getter(url, lo, hi):
    # The library passes the start and one-past-the-end values
    # for the range, just like a Python slice. So we need to
    # adjust the end value for the Range header.
    req = Request(url, headers={"Range": f"bytes={lo}-{hi-1}"})

    # Read the actual data
    with urlopen(req) as f:
        data = f.read()
        assert len(data) == hi-lo, f"Data ({lo}, {hi}) = {data!r}"

    return data

def open_url(url):
    url_getter = partial(getter, url)
    file_size = content_len(url)
    return LazyFile(file_size, url_getter)
```


```{toctree}
---
maxdepth: 2
caption: Contents
---
tutorial
howto
```

# Indices and tables

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search`
