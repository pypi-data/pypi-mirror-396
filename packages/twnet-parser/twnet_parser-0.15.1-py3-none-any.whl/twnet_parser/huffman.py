from twnet_parser.huffman_twnet_parser import huffman

LIBTW2_HUFFMAN = None

try:
    import libtw2_huffman as LIBTW2_HUFFMAN # type: ignore
except ImportError:
    LIBTW2_HUFFMAN = None

def backend_name() -> str:
    if LIBTW2_HUFFMAN:
        return 'rust-libtw2'
    return 'python-twnet_parser'

def compress(data: bytes) -> bytes:
    if LIBTW2_HUFFMAN:
        return LIBTW2_HUFFMAN.compress(data)
    return huffman.decompress(data)

def decompress(data: bytes) -> bytes:
    if LIBTW2_HUFFMAN:
        return LIBTW2_HUFFMAN.decompress(data)
    return huffman.decompress(data)
