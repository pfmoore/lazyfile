import sys
from urllib.request import Request, urlopen
from functools import partial
from lazyfile import LazyFile
from zipfile import ZipFile

# Get the metadata from a wheel by lazily reading just enough
# data from the URL.

def url_len(url):
    req = Request(url, method="HEAD")
    with urlopen(req) as f:
        return int(f.headers["Content-Length"])

def getter(url, lo, hi):
    req = Request(url, headers={"Range": f"bytes={lo}-{hi-1}"})
    with urlopen(req) as f:
        data = f.read()
        assert len(data) == hi-lo, f"Data ({lo}, {hi}) = {data!r}"
    return data

if __name__ == "__main__":
    g = partial(getter, sys.argv[1])
    size = url_len(sys.argv[1])
    f = LazyFile(size, g)
    z = ZipFile(f)
    for name in z.namelist():
        if name.endswith(".dist-info/METADATA"):
            print(z.read(name))
