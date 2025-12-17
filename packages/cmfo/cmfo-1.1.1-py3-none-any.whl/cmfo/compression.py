import zlib
import numpy as np
from .bridge import text_to_tensor


def compress_text(text: str) -> bytes:
    """
    Compresses text using a hybrid CMFO/Zlib approach.

    1. CMFO Layer: Converts text to semantic tensor (Signature).
       This acts as a 'checksum' or 'semantic hash' of the content.
    2. ENTROPY Layer: Uses DEFLATE (zlib) for lossless storage.

    *Future Vision:* In v2.0, the semantic tensor will allow
    lossy reconstruction without storing the raw text, achieving
    >100x compression for generic meaning.

    Current v1.0 implementation ensures lossless round-trip.
    """
    # 1. Semantic Signature (7 floats = 56 bytes)
    # We store this header to allow fast "semantic search" without
    # decompression.
    tensor = text_to_tensor(text)
    header = tensor.astype(np.float64).tobytes()  # 56 bytes

    # 2. Payload Compression
    payload = zlib.compress(text.encode('utf-8'), level=9)

    # Structure: [Header: 56 bytes] [Payload: N bytes]
    return header + payload


def decompress_text(data: bytes) -> str:
    """
    Decompresses CMFO binary format.
    """
    # Header is first 56 bytes (7 * 8)
    if len(data) < 56:
        raise ValueError("Invalid CMFO archive: Data too short")

    # We could read the tensor here if we wanted to verify integrity
    # tensor_bytes = data[:56]
    # tensor = np.frombuffer(tensor_bytes, dtype=np.float64)

    payload = data[56:]
    return zlib.decompress(payload).decode('utf-8')


def get_semantic_header(data: bytes) -> np.ndarray:
    """
    Extracts the semantic tensor WITHOUT decompressing the payload.
    This allows O(1) semantic search over compressed archives.
    """
    if len(data) < 56:
        raise ValueError("Invalid CMFO archive")
    return np.frombuffer(data[:56], dtype=np.float64)
