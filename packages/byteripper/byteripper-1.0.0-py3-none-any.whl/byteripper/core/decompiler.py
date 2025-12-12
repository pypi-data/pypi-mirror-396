import types
from byteripper.core.loader import pycloader
from byteripper.core.ast_builder import build_ast, astbuilder
from byteripper.core.codegen import generate_code
from byteripper.core.obfuscation import detect_obfuscation, get_raw_bytecode_dump
from byteripper.core.opcodes import disassemble_bytecode, format_instruction

class decompilationresult:
    def __init__(self):
        self.source_code = ""
        self.ast_tree = None
        self.bytecode_dump = ""
        self.errors = []
        self.warnings = []
        self.obfuscation_info = None
        self.debug_info = {}
        self.nested_functions = []
        self.nested_classes = []

def decompile(code_object, version_tuple=None, options=None):
    if options is None:
        options = {}
    result = decompilationresult()
    try:
        ast_tree, errors = build_ast(code_object, version_tuple)
        result.ast_tree = ast_tree
        result.errors.extend(errors)
        main_code = generate_code(ast_tree)
        nested_defs = []
        for const in code_object.co_consts:
            if isinstance(const, types.CodeType):
                if const.co_name.startswith("<"):
                    continue
                nested_result = decompile(const, version_tuple, options)
                result.nested_functions.append({
                    "name": const.co_name,
                    "result": nested_result
                })
                if _is_class_code(const):
                    class_def = _generate_class_def(const, nested_result, version_tuple)
                    if class_def:
                        nested_defs.append(class_def)
                else:
                    func_def = _generate_function_def(const, nested_result, version_tuple)
                    if func_def:
                        nested_defs.append(func_def)
        nested_defs = [d for d in nested_defs if d.strip()]
        main_code = _clean_main_code(main_code)
        if nested_defs:
            result.source_code = "\n\n".join(nested_defs) + "\n\n" + main_code
        else:
            result.source_code = main_code
    except exception as e:
        result.errors.append(f"decompilation failed: {str(e)}")
        result.source_code = f"# decompilation error: {str(e)}"
    return result

def _clean_main_code(code):
    lines = code.split("\n")
    clean_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped == "None":
            continue
        if stripped == "return None":
            continue
        if stripped == "print":
            continue
        if "= None(" in stripped:
            continue
        if stripped.endswith(" = None") and not "==" in stripped:
            continue
        if stripped.startswith("None(") and stripped.endswith(")"):
            inner = stripped[5:-1]
            clean_lines.append(inner)
            continue
        if " == " in stripped and not stripped.startswith("if "):
            clean_lines.append(f"if {stripped}:")
            clean_lines.append("    pass")
            continue
        clean_lines.append(line)
    return "\n".join(clean_lines)

def _generate_class_def(code_obj, decompiled_result, version_tuple):
    name = code_obj.co_name
    if name.startswith("<") and name.endswith(">"):
        return ""
    methods = []
    for const in code_obj.co_consts:
        if isinstance(const, types.CodeType):
            if const.co_name.startswith("<"):
                continue
            method_result = decompile(const, version_tuple, {})
            method_def = _generate_function_def(const, method_result, version_tuple)
            if method_def:
                method_lines = method_def.split("\n")
                indented = "\n".join("    " + line for line in method_lines)
                methods.append(indented)
    if not methods:
        methods.append("    pass")
    return f"class {name}:\n" + "\n\n".join(methods)

def _generate_function_def(code_obj, decompiled_result, version_tuple):
    name = code_obj.co_name
    if name.startswith("<") and name.endswith(">"):
        return ""
    args = []
    argcount = code_obj.co_argcount
    varnames = code_obj.co_varnames
    for i in range(argcount):
        if i < len(varnames):
            args.append(varnames[i])
    args_str = ", ".join(args)
    body = decompiled_result.source_code.strip()
    body_lines = [line for line in body.split("\n") if line.strip() and not _is_junk_line(line)]
    if not body_lines:
        body_lines = ["pass"]
    indented_body = "\n".join("    " + line for line in body_lines)
    return f"def {name}({args_str}):\n{indented_body}"

def _is_junk_line(line):
    junk_patterns = [
        "= None",
        "__module__ =",
        "__qualname__ =",
        "return None",
        "None",
    ]
    stripped = line.strip()
    if stripped == "None":
        return True
    if stripped == "return None":
        return True
    for pattern in junk_patterns:
        if pattern in stripped and "=" in stripped:
            parts = stripped.split("=")
            if len(parts) == 2 and parts[1].strip() == "None":
                return True
    return False

def _is_class_code(code_obj):
    names = code_obj.co_names
    if "__module__" in names and "__qualname__" in names:
        has_nested_funcs = False
        for const in code_obj.co_consts:
            if isinstance(const, types.CodeType):
                if not const.co_name.startswith("<"):
                    has_nested_funcs = True
                    break
        return has_nested_funcs
    return False

def decompile_file(filepath, options=None):
    if options is None:
        options = {}
    loader = pycloader(filepath)
    if loader.errors:
        result = decompilationresult()
        result.errors.extend(loader.errors)
        return result
    result = decompilationresult()
    if options.get("check_obfuscation", True):
        result.obfuscation_info = detect_obfuscation(loader)
        if result.obfuscation_info["is_obfuscated"] and not options.get("force", False):
            result.warnings.append("file appears to be obfuscated")
            if not result.obfuscation_info["can_decompile"]:
                result.source_code = "# obfuscated file - cannot decompile\n"
                result.source_code += "# raw bytecode dump:\n"
                result.source_code += get_raw_bytecode_dump(loader)
                return result
    if options.get("debug", False):
        result.debug_info["header"] = loader.debug_dump()
    if options.get("show_bytecode", False):
        instructions = disassemble_bytecode(loader.code_object, loader.version_tuple)
        lines = []
        for instr in instructions:
            lines.append(format_instruction(instr, loader.code_object))
        result.bytecode_dump = "\n".join(lines)
    code_result = decompile(loader.code_object, loader.version_tuple, options)
    result.source_code = code_result.source_code
    result.ast_tree = code_result.ast_tree
    result.errors.extend(code_result.errors)
    result.nested_functions = code_result.nested_functions
    return result

def get_bytecode_dump(filepath):
    loader = pycloader(filepath)
    if loader.errors or not loader.code_object:
        return "failed to load file"
    instructions = disassemble_bytecode(loader.code_object, loader.version_tuple)
    lines = []
    lines.append(f"# bytecode dump for: {filepath}")
    lines.append(f"# python version: {loader.version}")
    lines.append("-" * 60)
    for instr in instructions:
        lines.append(format_instruction(instr, loader.code_object))
    return "\n".join(lines)

def get_ast_dump(filepath):
    loader = pycloader(filepath)
    if loader.errors or not loader.code_object:
        return "failed to load file"
    import ast
    ast_tree, errors = build_ast(loader.code_object, loader.version_tuple)
    try:
        return ast.dump(ast_tree, indent=2)
    except exception:
        return ast.dump(ast_tree)

exception = Exception
