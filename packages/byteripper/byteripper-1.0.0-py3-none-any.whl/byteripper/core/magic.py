magic_numbers = {
    3350: (3, 5, 0),
    3351: (3, 5, 1),
    3352: (3, 5, 2),
    3360: (3, 6, 0),
    3361: (3, 6, 1),
    3370: (3, 7, 0),
    3371: (3, 7, 1),
    3372: (3, 7, 2),
    3373: (3, 7, 3),
    3374: (3, 7, 4),
    3375: (3, 7, 5),
    3376: (3, 7, 6),
    3377: (3, 7, 7),
    3378: (3, 7, 8),
    3379: (3, 7, 9),
    3390: (3, 8, 0),
    3391: (3, 8, 1),
    3392: (3, 8, 2),
    3393: (3, 8, 3),
    3394: (3, 8, 4),
    3395: (3, 8, 5),
    3400: (3, 9, 0),
    3401: (3, 9, 1),
    3410: (3, 10, 0),
    3411: (3, 10, 1),
    3412: (3, 10, 2),
    3413: (3, 10, 3),
    3420: (3, 11, 0),
    3421: (3, 11, 1),
    3422: (3, 11, 2),
    3423: (3, 11, 3),
    3424: (3, 11, 4),
    3425: (3, 11, 5),
    3426: (3, 11, 6),
    3427: (3, 11, 7),
    3428: (3, 11, 8),
    3429: (3, 11, 9),
    3430: (3, 12, 0),
    3431: (3, 12, 1),
    3432: (3, 12, 2),
    3433: (3, 12, 3),
    3434: (3, 12, 4),
    3435: (3, 12, 5),
    3436: (3, 12, 6),
    3440: (3, 13, 0),
    3441: (3, 13, 1),
    3442: (3, 13, 2),
    3443: (3, 13, 3),
    3450: (3, 14, 0),
    3451: (3, 14, 1),
    3490: (3, 11, 10),
    3491: (3, 11, 11),
    3492: (3, 11, 12),
    3493: (3, 11, 13),
    3494: (3, 11, 14),
    3495: (3, 11, 13),
    3496: (3, 11, 14),
    3497: (3, 11, 15),
    3498: (3, 11, 16),
    3499: (3, 11, 17),
}

magic_to_version_str = {}
for magic, ver in magic_numbers.items():
    magic_to_version_str[magic] = f"{ver[0]}.{ver[1]}"

def get_magic_number(data):
    if len(data) < 4:
        return None
    magic = data[0] | (data[1] << 8)
    return magic

def get_python_version(magic):
    if magic in magic_numbers:
        ver = magic_numbers[magic]
        return f"{ver[0]}.{ver[1]}.{ver[2]}"
    for m, v in magic_numbers.items():
        if abs(magic - m) <= 10:
            return f"{v[0]}.{v[1]}"
    return "unknown"

def get_version_tuple(magic):
    if magic in magic_numbers:
        return magic_numbers[magic]
    for m, v in magic_numbers.items():
        if abs(magic - m) <= 10:
            return v
    return (3, 11, 0)

def is_valid_magic(magic):
    return magic in magic_numbers or any(abs(magic - m) <= 10 for m in magic_numbers.keys())

def detect_header_size(data, magic):
    version = get_version_tuple(magic)
    if version >= (3, 7):
        if len(data) >= 8:
            flags = data[4] | (data[5] << 8) | (data[6] << 16) | (data[7] << 24)
            if flags & 1:
                return 16
            return 16
    if version >= (3, 3):
        return 12
    return 8

def get_header_info(data):
    if len(data) < 8:
        return None
    magic = get_magic_number(data)
    version = get_version_tuple(magic)
    info = {
        "magic": magic,
        "magic_hex": hex(magic),
        "version": get_python_version(magic),
        "version_tuple": version,
    }
    if version >= (3, 7):
        if len(data) >= 16:
            flags = data[4] | (data[5] << 8) | (data[6] << 16) | (data[7] << 24)
            info["flags"] = flags
            info["hash_based"] = bool(flags & 1)
            if flags & 1:
                info["check_source"] = bool(flags & 2)
                info["hash"] = data[8:16].hex()
            else:
                timestamp = data[8] | (data[9] << 8) | (data[10] << 16) | (data[11] << 24)
                size = data[12] | (data[13] << 8) | (data[14] << 16) | (data[15] << 24)
                info["timestamp"] = timestamp
                info["source_size"] = size
            info["header_size"] = 16
    elif version >= (3, 3):
        if len(data) >= 12:
            timestamp = data[4] | (data[5] << 8) | (data[6] << 16) | (data[7] << 24)
            size = data[8] | (data[9] << 8) | (data[10] << 16) | (data[11] << 24)
            info["timestamp"] = timestamp
            info["source_size"] = size
            info["header_size"] = 12
    else:
        if len(data) >= 8:
            timestamp = data[4] | (data[5] << 8) | (data[6] << 16) | (data[7] << 24)
            info["timestamp"] = timestamp
            info["header_size"] = 8
    return info
