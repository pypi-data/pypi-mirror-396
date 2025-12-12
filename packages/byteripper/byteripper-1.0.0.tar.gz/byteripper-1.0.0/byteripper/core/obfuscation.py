from byteripper.core.magic import is_valid_magic, get_magic_number

def detect_obfuscation(loader):
    result = {
        "is_obfuscated": False,
        "confidence": 0,
        "reasons": [],
        "obfuscation_type": None,
        "can_decompile": True,
    }
    if not loader.raw_data:
        result["is_obfuscated"] = True
        result["confidence"] = 100
        result["reasons"].append("no data available")
        result["can_decompile"] = False
        return result
    magic = get_magic_number(loader.raw_data)
    if not is_valid_magic(magic):
        result["is_obfuscated"] = True
        result["confidence"] += 40
        result["reasons"].append(f"invalid magic number: {hex(magic)}")
        result["obfuscation_type"] = "encrypted_header"
    if loader.code_object is None:
        result["is_obfuscated"] = True
        result["confidence"] += 50
        result["reasons"].append("failed to unmarshal code object")
        result["can_decompile"] = False
        return result
    code = loader.code_object
    if hasattr(code, "co_code"):
        bytecode = code.co_code
        null_count = bytecode.count(b"\x00"[0]) if isinstance(bytecode, bytes) else 0
        if len(bytecode) > 0 and null_count / len(bytecode) > 0.7:
            result["is_obfuscated"] = True
            result["confidence"] += 20
            result["reasons"].append("high null byte ratio in bytecode")
    if hasattr(code, "co_names"):
        obfuscated_names = 0
        for name in code.co_names:
            if _is_obfuscated_name(name):
                obfuscated_names += 1
        if len(code.co_names) > 0 and obfuscated_names / len(code.co_names) > 0.3:
            result["is_obfuscated"] = True
            result["confidence"] += 15
            result["reasons"].append("obfuscated variable names detected")
            result["obfuscation_type"] = "name_mangling"
    if hasattr(code, "co_consts"):
        encrypted_strings = 0
        for const in code.co_consts:
            if isinstance(const, (str, bytes)) and _looks_encrypted(const):
                encrypted_strings += 1
        if encrypted_strings > 3:
            result["is_obfuscated"] = True
            result["confidence"] += 20
            result["reasons"].append("encrypted strings detected in constants")
            result["obfuscation_type"] = "string_encryption"
    known_patterns = _check_known_obfuscators(loader)
    if known_patterns:
        result["is_obfuscated"] = True
        result["confidence"] += 25
        result["reasons"].extend(known_patterns)
        result["obfuscation_type"] = "known_obfuscator"
    result["confidence"] = min(result["confidence"], 100)
    return result

def _is_obfuscated_name(name):
    if not isinstance(name, str):
        return False
    if len(name) > 30 and all(c in "abcdef0123456789" for c in name.lower()):
        return True
    if name.startswith("_0x") or name.startswith("0x"):
        return True
    if all(c == "_" or c.isdigit() for c in name) and len(name) > 5:
        return True
    if name.count("_") > len(name) / 2 and len(name) > 10:
        return True
    return False

def _looks_encrypted(data):
    if isinstance(data, str):
        data = data.encode("utf-8", errors="ignore")
    if len(data) < 10:
        return False
    printable = sum(1 for b in data if 32 <= b <= 126)
    if printable / len(data) < 0.3:
        return True
    return False

def _check_known_obfuscators(loader):
    patterns = []
    if loader.code_object:
        code = loader.code_object
        consts_str = str(code.co_consts)
        names_str = str(code.co_names)
        if "pyarmor" in consts_str.lower() or "pyarmor" in names_str.lower():
            patterns.append("pyarmor obfuscation detected")
        if "pytransform" in names_str.lower():
            patterns.append("pytransform layer detected")
        if "_pjorion" in names_str.lower() or "pjorion" in consts_str.lower():
            patterns.append("pjorion obfuscation detected")
        if "__pyc_" in names_str:
            patterns.append("possible custom obfuscator detected")
    return patterns

def get_obfuscation_report(loader):
    result = detect_obfuscation(loader)
    lines = []
    lines.append("=" * 60)
    lines.append("obfuscation analysis report")
    lines.append("=" * 60)
    lines.append(f"status: {'obfuscated' if result['is_obfuscated'] else 'clean'}")
    lines.append(f"confidence: {result['confidence']}%")
    if result["obfuscation_type"]:
        lines.append(f"type: {result['obfuscation_type']}")
    lines.append(f"can decompile: {'yes' if result['can_decompile'] else 'no'}")
    if result["reasons"]:
        lines.append("-" * 60)
        lines.append("findings:")
        for reason in result["reasons"]:
            lines.append(f"  - {reason}")
    lines.append("=" * 60)
    return "\n".join(lines)

def get_raw_bytecode_dump(loader):
    if not loader.code_object:
        return "no code object available"
    lines = []
    lines.append("raw bytecode dump:")
    lines.append("-" * 40)
    bytecode = loader.code_object.co_code
    for i in range(0, len(bytecode), 16):
        chunk = bytecode[i:i + 16]
        hex_str = " ".join(f"{b:02x}" for b in chunk)
        ascii_str = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
        lines.append(f"{i:04x}: {hex_str:<48} {ascii_str}")
    return "\n".join(lines)
