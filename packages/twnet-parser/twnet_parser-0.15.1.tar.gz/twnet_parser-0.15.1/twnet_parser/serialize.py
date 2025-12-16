def bytes_to_hex(obj):
    if isinstance(obj, bytes):
        return obj.hex()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

