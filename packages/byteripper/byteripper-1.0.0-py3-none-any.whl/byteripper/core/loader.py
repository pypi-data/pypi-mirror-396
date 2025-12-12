import marshal
import struct
import types
from byteripper.core.magic import (
    get_magic_number,
    get_python_version,
    get_version_tuple,
    detect_header_size,
    get_header_info,
    is_valid_magic,
)

class pycloader:
    def __init__(self, filepath=None, data=None):
        self.filepath = filepath
        self.raw_data = data
        self.magic = None
        self.version = None
        self.version_tuple = None
        self.header_info = None
        self.header_size = 0
        self.code_object = None
        self.errors = []
        self.warnings = []
        if filepath:
            self.load_file(filepath)
        elif data:
            self.load_data(data)

    def load_file(self, filepath):
        try:
            with open(filepath, "rb") as f:
                self.raw_data = f.read()
            self._parse()
        except exception as e:
            self.errors.append(f"failed to load file: {str(e)}")

    def load_data(self, data):
        self.raw_data = data
        self._parse()

    def _parse(self):
        if not self.raw_data or len(self.raw_data) < 8:
            self.errors.append("invalid pyc file: too small")
            return
        self.magic = get_magic_number(self.raw_data)
        if not is_valid_magic(self.magic):
            self.warnings.append(f"unknown magic number: {self.magic}")
        self.version = get_python_version(self.magic)
        self.version_tuple = get_version_tuple(self.magic)
        self.header_info = get_header_info(self.raw_data)
        self.header_size = detect_header_size(self.raw_data, self.magic)
        self._load_code_object()

    def _load_code_object(self):
        try:
            code_data = self.raw_data[self.header_size:]
            self.code_object = marshal.loads(code_data)
        except exception as e:
            self.errors.append(f"failed to unmarshal code object: {str(e)}")
            self.code_object = None

    def get_code_object(self):
        return self.code_object

    def get_bytecode(self):
        if self.code_object:
            return self.code_object.co_code
        return None

    def get_constants(self):
        if self.code_object:
            return self.code_object.co_consts
        return ()

    def get_names(self):
        if self.code_object:
            return self.code_object.co_names
        return ()

    def get_varnames(self):
        if self.code_object:
            return self.code_object.co_varnames
        return ()

    def get_filename(self):
        if self.code_object:
            return self.code_object.co_filename
        return ""

    def get_name(self):
        if self.code_object:
            return self.code_object.co_name
        return ""

    def get_all_code_objects(self):
        result = []
        def collect(code):
            result.append(code)
            for const in code.co_consts:
                if isinstance(const, types.CodeType):
                    collect(const)
        if self.code_object:
            collect(self.code_object)
        return result

    def debug_dump(self):
        lines = []
        lines.append("=" * 60)
        lines.append("byteripper debug dump")
        lines.append("=" * 60)
        if self.header_info:
            lines.append(f"magic number: {self.header_info.get('magic_hex', 'n/a')}")
            lines.append(f"python version: {self.header_info.get('version', 'n/a')}")
            lines.append(f"header size: {self.header_info.get('header_size', 'n/a')} bytes")
            if "flags" in self.header_info:
                lines.append(f"flags: {self.header_info['flags']}")
            if "timestamp" in self.header_info:
                lines.append(f"timestamp: {self.header_info['timestamp']}")
            if "source_size" in self.header_info:
                lines.append(f"source size: {self.header_info['source_size']} bytes")
            if "hash_based" in self.header_info and self.header_info["hash_based"]:
                lines.append(f"hash: {self.header_info.get('hash', 'n/a')}")
        lines.append("-" * 60)
        if self.code_object:
            lines.append("code object info:")
            lines.append(f"  name: {self.code_object.co_name}")
            lines.append(f"  filename: {self.code_object.co_filename}")
            lines.append(f"  argcount: {self.code_object.co_argcount}")
            lines.append(f"  kwonlyargcount: {self.code_object.co_kwonlyargcount}")
            if hasattr(self.code_object, "co_posonlyargcount"):
                lines.append(f"  posonlyargcount: {self.code_object.co_posonlyargcount}")
            lines.append(f"  nlocals: {self.code_object.co_nlocals}")
            lines.append(f"  stacksize: {self.code_object.co_stacksize}")
            lines.append(f"  flags: {self.code_object.co_flags}")
            lines.append(f"  code size: {len(self.code_object.co_code)} bytes")
            lines.append(f"  constants: {len(self.code_object.co_consts)}")
            lines.append(f"  names: {self.code_object.co_names}")
            lines.append(f"  varnames: {self.code_object.co_varnames}")
        lines.append("=" * 60)
        if self.errors:
            lines.append("errors:")
            for e in self.errors:
                lines.append(f"  - {e}")
        if self.warnings:
            lines.append("warnings:")
            for w in self.warnings:
                lines.append(f"  - {w}")
        return "\n".join(lines)

exception = Exception
