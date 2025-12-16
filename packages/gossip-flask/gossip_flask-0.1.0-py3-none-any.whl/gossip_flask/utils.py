from __future__ import annotations

import math
from collections import Counter
from typing import ByteString


# https://stackoverflow.com/questions/43787031/python-byte-array-to-bit-array
def access_bit(data, num):
    base = int(num // 8)
    shift = int(num % 8)
    return (data[base] >> shift) & 0x1


def bytes_to_bits(data: ByteString) -> list[int]:
    return [access_bit(data, i) for i in range(len(data) * 8)]
