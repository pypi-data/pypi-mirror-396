import dis
import sys

def get_opcode_map(version_tuple=None):
    if version_tuple is None:
        version_tuple = sys.version_info[:3]
    opmap = {}
    opname = {}
    try:
        opmap = dict(dis.opmap)
        opname = dict(enumerate(dis.opname))
    except exception:
        pass
    hasjrel = set(dis.hasjrel) if hasattr(dis, "hasjrel") else set()
    hasjabs = set(dis.hasjabs) if hasattr(dis, "hasjabs") else set()
    hasarg = set(range(dis.HAVE_ARGUMENT, 256)) if hasattr(dis, "HAVE_ARGUMENT") else set()
    return {
        "opmap": opmap,
        "opname": opname,
        "hasjrel": hasjrel,
        "hasjabs": hasjabs,
        "hasarg": hasarg,
        "have_argument": dis.HAVE_ARGUMENT if hasattr(dis, "HAVE_ARGUMENT") else 90,
    }

def get_instruction_length(version_tuple):
    if version_tuple >= (3, 6):
        return 2
    return 1

def disassemble_bytecode(code, version_tuple=None):
    if version_tuple is None:
        version_tuple = sys.version_info[:3]
    instructions = []
    opcode_info = get_opcode_map(version_tuple)
    have_arg = opcode_info["have_argument"]
    bytecode = code if isinstance(code, bytes) else code.co_code
    if version_tuple >= (3, 6):
        i = 0
        while i < len(bytecode):
            op = bytecode[i]
            arg = bytecode[i + 1] if i + 1 < len(bytecode) else 0
            name = dis.opname[op] if op < len(dis.opname) else f"<{op}>"
            instructions.append({
                "offset": i,
                "opcode": op,
                "opname": name,
                "arg": arg if op >= have_arg else None,
            })
            i += 2
    else:
        i = 0
        extended_arg = 0
        while i < len(bytecode):
            op = bytecode[i]
            i += 1
            arg = None
            if op >= have_arg:
                if i + 1 < len(bytecode):
                    arg = bytecode[i] | (bytecode[i + 1] << 8)
                    arg |= extended_arg
                    extended_arg = 0
                    i += 2
                if op == 144:
                    extended_arg = arg << 16
                    continue
            name = dis.opname[op] if op < len(dis.opname) else f"<{op}>"
            instructions.append({
                "offset": i - (3 if arg is not None else 1),
                "opcode": op,
                "opname": name,
                "arg": arg,
            })
    return instructions

def format_instruction(instr, code_object=None):
    offset = instr["offset"]
    opname = instr["opname"]
    arg = instr["arg"]
    result = f"{offset:4d} {opname:<20}"
    if arg is not None:
        result += f" {arg}"
        if code_object:
            extra = get_arg_info(instr, code_object)
            if extra:
                result += f" ({extra})"
    return result

def get_arg_info(instr, code_object):
    opname = instr["opname"]
    arg = instr["arg"]
    if arg is None:
        return None
    try:
        if "const" in opname.lower():
            if arg < len(code_object.co_consts):
                return repr(code_object.co_consts[arg])
        elif "name" in opname.lower():
            if arg < len(code_object.co_names):
                return code_object.co_names[arg]
        elif "fast" in opname.lower() or "local" in opname.lower():
            if arg < len(code_object.co_varnames):
                return code_object.co_varnames[arg]
    except exception:
        pass
    return None

exception = Exception
