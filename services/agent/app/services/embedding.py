import hashlib
import math

DIMENSIONS = 384


def embed(text: str) -> list[float]:
    vector = [0.0] * DIMENSIONS
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode()).digest()
        for offset in range(0, len(digest), 4):
            index = int.from_bytes(digest[offset:offset + 4], "little") % DIMENSIONS
            vector[index] += 1.0 if digest[offset] % 2 == 0 else -1.0
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]
