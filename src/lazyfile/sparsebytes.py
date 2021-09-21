import operator

from spans import intrange, intrangeset


class InvalidGetter(Exception):
    """Raised when a getter doesn't conform to requirements"""


class SparseBytes:
    """A byte array that is loaded "on demand".

    An indexable array of bytes that only requests the actual
    bytes of data from the underlying data source when required.
    """

    def __init__(self, size, getter):
        self.size = size
        self.getter = getter

        # A list of blocks of data that have been loaded.
        # The list contains tuples, (lo, hi, chunk). Each entry
        # holds the data for range lo:hi in the array.
        # Blocks are sorted in ascending order of starting index,
        # no two blocks overlap and in addition, all blocks are
        # as large as possible, so there is always a gap between
        # any pair of blocks.
        self.blocks = []

    def _get(self, lo, hi):
        """Get data. Ensures the result is the right length.

        If the getter raises an exception, this is passed on to the caller.
        """
        result = self.getter(lo, hi)
        if len(result) != hi - lo:
            raise InvalidGetter(f"Requested {hi-lo} bytes, got {len(result)}")
        return result

    def _coalesce(self):
        # Re-establish the invariant that self.blocks is sorted,
        # and every pair of blocks has a gap between them.

        if len(self.blocks) == 0:
            # Nothing to do
            return

        # Ensure blocks are ordered correctly
        self.blocks.sort()

        # Merge any adjacent pairs of blocks with no gap between them
        blocks = self.blocks
        new_blocks = []
        lo, hi, chunk = blocks.pop(0)
        while blocks:
            next_lo, next_hi, next_chunk = blocks.pop(0)
            if hi == next_lo:
                # Merge two adjacent chunks
                hi = next_hi
                chunk += next_chunk
            else:
                new_blocks.append((lo, hi, chunk))
                lo = next_lo
                hi = next_hi
                chunk = next_chunk
        new_blocks.append((lo, hi, chunk))
        self.blocks = new_blocks

    def ensure(self, lo, hi):
        """Ensure that the range lo:hi is loaded"""

        # Calculate the set of ranges that we need which are not
        # already loaded
        need = intrangeset([intrange(lo, hi)])
        need = need.difference(intrangeset(intrange(l, h) for l, h, _ in self.blocks))

        # Get each needed block and add it to the block list. At
        # this point, just append it at the end, we will re-establish
        # the invariant once we are finished.
        for part_range in need:
            part_lo = part_range.lower
            part_hi = part_range.upper
            part = self._get(part_lo, part_hi)
            self.blocks.append((part_lo, part_hi, part))

        self._coalesce()

    def __len__(self):
        """The length of the array"""
        return self.size

    def __getitem__(self, key):
        """Get data from the array"""

        # Are we reading a single item, rather than a range?
        if not isinstance(key, slice):
            key = operator.index(key)

            # Handle negative indices, then make sure the request is in range
            if key < 0:
                key = self.size + key
            if not (0 <= key < self.size):
                raise IndexError("index out of range")

            # Make sure the requested byte is present
            self.ensure(key, key + 1)

            # Find the correct data block and return the requested byte
            for lo, hi, part in self.blocks:
                if lo <= key < hi:
                    return part[key - lo]

            # We should never fall off the end of the loop
            assert False, "Failed to ensure requested byte"  # pragma: no cover

        # If we get here, it's a slice request
        # Get the byte range and step in normalised form
        lo, hi, step = key.indices(self.size)

        # Special case 0-byte request, as there's nothing to get
        if hi == lo:
            return b""

        # Make sure we have the required range. Note that the
        # invariant for self.blocks means that the resulting range
        # will be completely within one element of the blocks array.
        self.ensure(lo, hi)

        # Find the correct block and extract the requested data
        result = None
        for l, h, data in self.blocks:
            if l <= lo < h:
                assert hi <= h, "Failed to ensure a single block"
                result = data[lo - l : hi - l : step]
                break
        # We should always find something, as that's the contract
        # for ensure.
        assert result is not None, "Failed to ensure requested bytes"
        return result
