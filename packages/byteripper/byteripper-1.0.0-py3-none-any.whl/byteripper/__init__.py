__version__ = "1.0.0"
__author__ = "mero"
__telegram__ = "qp4rm"
__github__ = "6x-u"

from byteripper.core.loader import pycloader
from byteripper.core.decompiler import decompile, decompile_file
from byteripper.core.magic import get_python_version, magic_numbers
from byteripper.core.obfuscation import detect_obfuscation
from byteripper.core.ast_builder import build_ast
from byteripper.core.codegen import generate_code

__all__ = [
    "pycloader",
    "decompile",
    "decompile_file",
    "get_python_version",
    "magic_numbers",
    "detect_obfuscation",
    "build_ast",
    "generate_code",
    "__version__",
    "__author__",
]

def ready_message():
    print("i'm ready")
