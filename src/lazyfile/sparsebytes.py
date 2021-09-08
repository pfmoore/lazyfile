from spans import intrange, intrangeset
import operator

# SparseBytes
# ===========
#
# size = N
# blocks = [(lo, hi, bytes), ...]
# filled = intrangeset(intrange(lo, hi) for lo, hi, _ in blocks)
# gaps = intrangeset(intrange(0, N)).difference(filled)
#
# ensure(lo, hi):
#     need = gaps.intersection(intrangeset([intrange(lo, hi)]))
#     for part_lo, part_hi in need:
#         part = get_bytes(part_lo, part_hi)
#         blocks.append((part_lo, part_hi, part))
#     coalesce(blocks)
#
# coalesce(blocks):
#     # Re-sort blocks, merging adjacent chunks
#     blocks.sort()
#     lo, hi, chunk = blocks.pop(0)
#     new_blocks = []
#     while blocks:
#         next_lo, next_hi, next_chunk = blocks.pop(0)
#         if hi == next_lo:
#             # Merge
#             hi = next_hi
#             chunk += next_chunk
#         else:
#             new_blocks.append((lo, hi, chunk))
#             lo, hi, chunk = next_lo, next_hi, next_chunk
#     new_blocks.append((lo, hi, chunk))
#     return new_blocks

class SparseBytes:
    def __init__(self, size, getter):
        self.size = size
        self.blocks = []
        self.getter = getter

    def _coalesce(self):
        # Re-establish the invariant that self.blocks is sorted,
        # and every pair of blocks has a gap between them.

        if len(self.blocks) == 0:
            # Nothing to do
            return

        self.blocks.sort()
        blocks = self.blocks
        new_blocks = []
        lo, hi, chunk = blocks.pop(0)
        while blocks:
            next_lo, next_hi, next_chunk = blocks.pop(0)
            if hi == next_lo:
                # Merge two adhacent chunks
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
        need = intrangeset([intrange(lo, hi)])
        need = need.difference(intrangeset(intrange(l, h) for l, h, _ in self.blocks))
        for part_range in need:
            part_lo = part_range.lower
            part_hi = part_range.upper
            part = self.getter(part_lo, part_hi)
            self.blocks.append((part_lo, part_hi, part))
        self._coalesce()

    def __len__(self):
        return self.size

    def __getitem__(self, key):
        if not isinstance(key, slice):
            key = operator.index(key)
            if key < 0:
                key = self.size + key
            if not (0 <= key < self.size):
                raise IndexError("index out of range")
            self.ensure(key, key + 1)
            for lo, hi, part in self.blocks:
                if lo <= key < hi:
                    return part[key - lo]
            else:
                raise RuntimeError("Failed to ensure requested byte")

        # If we get here, it's a slice request
        lo, hi, step = key.indices(self.size)

        # Special case 0-byte request, as there's nothing to get
        if hi == lo:
            return b''

        self.ensure(lo, hi)
        result = None
        for l, h, data in self.blocks:
            if l <= lo < h:
                assert hi <= h, "Failed to ensure a single block"
                result = data[lo - l : hi - l : step]
                break

        assert result is not None, "Failed to load requested bytes"
        return result