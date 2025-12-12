import argparse
import sys
import os
from byteripper import __version__, __author__, __telegram__, __github__
from byteripper.core.loader import pycloader
from byteripper.core.decompiler import decompile_file, get_bytecode_dump, get_ast_dump
from byteripper.core.obfuscation import get_obfuscation_report, get_raw_bytecode_dump
from byteripper.core.ai_cleanup import cleanup_code, is_ai_available

def create_parser():
    parser = argparse.ArgumentParser(
        prog="byteripper",
        description="python bytecode decompiler - pyc to py converter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
examples:
  byteripper input.pyc                    decompile to stdout
  byteripper input.pyc -o output.py       decompile to file
  byteripper input.pyc --show-bytecode    show bytecode instructions
  byteripper input.pyc --show-ast         show ast tree
  byteripper input.pyc --debug            show debug info
  byteripper input.pyc --check-obfuscation  check if file is obfuscated
  byteripper input.pyc --ai-cleanup       use ai to clean up code

version: {__version__}
author: {__author__}
telegram: {__telegram__}
github: {__github__}
"""
    )
    parser.add_argument("input", nargs="?", help="input pyc file")
    parser.add_argument("-o", "--output", help="output file path")
    parser.add_argument("-v", "--version", action="store_true", help="show version")
    parser.add_argument("--show-bytecode", action="store_true", help="show bytecode instructions")
    parser.add_argument("--show-ast", action="store_true", help="show ast tree")
    parser.add_argument("--debug", action="store_true", help="show debug information")
    parser.add_argument("--force", action="store_true", help="force decompilation even if obfuscated")
    parser.add_argument("--check-obfuscation", action="store_true", help="check for obfuscation")
    parser.add_argument("--raw-bytecode", action="store_true", help="dump raw bytecode")
    parser.add_argument("--ai-cleanup", action="store_true", help="use ai to clean up decompiled code")
    parser.add_argument("--ai-model", default="gpt-4o-mini", help="ai model to use for cleanup")
    parser.add_argument("--target-version", help="target python version (e.g. 3.11)")
    parser.add_argument("--no-nested", action="store_true", help="skip nested functions/classes")
    parser.add_argument("--quiet", action="store_true", help="suppress warnings")
    parser.add_argument("--header-only", action="store_true", help="show only header information")
    parser.add_argument("--constants", action="store_true", help="show constants")
    parser.add_argument("--names", action="store_true", help="show names")
    parser.add_argument("--varnames", action="store_true", help="show variable names")
    parser.add_argument("--all-code-objects", action="store_true", help="list all code objects")
    parser.add_argument("--disassemble", action="store_true", help="show disassembly")
    parser.add_argument("--verify", action="store_true", help="verify decompiled code syntax")
    parser.add_argument("--batch", action="store_true", help="batch mode for multiple files")
    parser.add_argument("--recursive", action="store_true", help="process directories recursively")
    parser.add_argument("--extension", default=".py", help="output file extension")
    parser.add_argument("--indent", type=int, default=4, help="indentation size")
    parser.add_argument("--line-numbers", action="store_true", help="add line numbers to output")
    parser.add_argument("--no-header", action="store_true", help="skip file header comment")
    parser.add_argument("--json", action="store_true", help="output as json")
    parser.add_argument("--stats", action="store_true", help="show decompilation statistics")
    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()
    if args.version:
        print(f"byteripper version {__version__}")
        print(f"author: {__author__}")
        print(f"telegram: {__telegram__}")
        print(f"github: {__github__}")
        return 0
    if not args.input:
        parser.print_help()
        return 1
    if not os.path.exists(args.input):
        print(f"error: file not found: {args.input}")
        return 1
    if args.batch or args.recursive:
        return process_batch(args)
    return process_single(args)

def process_single(args):
    loader = pycloader(args.input)
    if loader.errors:
        for err in loader.errors:
            print(f"error: {err}")
        return 1
    if args.header_only:
        print(loader.debug_dump())
        return 0
    if args.check_obfuscation:
        print(get_obfuscation_report(loader))
        return 0
    if args.raw_bytecode:
        print(get_raw_bytecode_dump(loader))
        return 0
    if args.constants:
        print("constants:")
        for i, const in enumerate(loader.get_constants()):
            print(f"  {i}: {repr(const)}")
        return 0
    if args.names:
        print("names:")
        for i, name in enumerate(loader.get_names()):
            print(f"  {i}: {name}")
        return 0
    if args.varnames:
        print("varnames:")
        for i, name in enumerate(loader.get_varnames()):
            print(f"  {i}: {name}")
        return 0
    if args.all_code_objects:
        print("code objects:")
        for i, code in enumerate(loader.get_all_code_objects()):
            print(f"  {i}: {code.co_name} ({code.co_filename})")
        return 0
    if args.show_bytecode or args.disassemble:
        print(get_bytecode_dump(args.input))
        return 0
    if args.show_ast:
        print(get_ast_dump(args.input))
        return 0
    if args.debug:
        print(loader.debug_dump())
        print()
    options = {
        "force": args.force,
        "debug": args.debug,
        "show_bytecode": args.show_bytecode,
        "check_obfuscation": not args.force,
    }
    result = decompile_file(args.input, options)
    if not args.quiet:
        for warn in result.warnings:
            print(f"warning: {warn}", file=sys.stderr)
    for err in result.errors:
        print(f"error: {err}", file=sys.stderr)
    source = result.source_code
    if args.ai_cleanup:
        if is_ai_available():
            source, ai_error = cleanup_code(source, args.ai_model)
            if ai_error and not args.quiet:
                print(f"warning: {ai_error}", file=sys.stderr)
        elif not args.quiet:
            print("warning: g4f not available for ai cleanup", file=sys.stderr)
    if args.verify:
        try:
            compile(source, "<string>", "exec")
            if not args.quiet:
                print("syntax verification: ok", file=sys.stderr)
        except syntaxerror as e:
            print(f"syntax error: {e}", file=sys.stderr)
    if args.line_numbers:
        lines = source.split("\n")
        source = "\n".join(f"{i+1:4d}: {line}" for i, line in enumerate(lines))
    if not args.no_header:
        header = f"# decompiled by byteripper v{__version__}\n"
        header += f"# original file: {args.input}\n"
        header += f"# python version: {loader.version}\n\n"
        source = header + source
    if args.json:
        import json
        output = {
            "source": source,
            "version": loader.version,
            "errors": result.errors,
            "warnings": result.warnings,
        }
        source = json.dumps(output, indent=2)
    if args.output:
        with open(args.output, "w") as f:
            f.write(source)
        print(f"decompiled to: {args.output}")
    else:
        print(source)
    if args.stats:
        print("\nstatistics:", file=sys.stderr)
        print(f"  source lines: {len(source.splitlines())}", file=sys.stderr)
        print(f"  errors: {len(result.errors)}", file=sys.stderr)
        print(f"  warnings: {len(result.warnings)}", file=sys.stderr)
    return 0 if not result.errors else 1

def process_batch(args):
    import glob
    if args.recursive:
        pattern = os.path.join(args.input, "**", "*.pyc")
        files = glob.glob(pattern, recursive=True)
    else:
        if os.path.isdir(args.input):
            pattern = os.path.join(args.input, "*.pyc")
            files = glob.glob(pattern)
        else:
            files = [args.input]
    total = len(files)
    success = 0
    failed = 0
    for i, filepath in enumerate(files):
        print(f"[{i+1}/{total}] processing: {filepath}")
        try:
            result = decompile_file(filepath, {"force": args.force})
            if args.output:
                outdir = args.output
            else:
                outdir = os.path.dirname(filepath)
            basename = os.path.splitext(os.path.basename(filepath))[0]
            outpath = os.path.join(outdir, basename + args.extension)
            os.makedirs(os.path.dirname(outpath), exist_ok=True)
            with open(outpath, "w") as f:
                f.write(result.source_code)
            success += 1
        except exception as e:
            print(f"  failed: {e}")
            failed += 1
    print(f"\nbatch complete: {success} success, {failed} failed")
    return 0 if failed == 0 else 1

def ready():
    print("i'm ready")

if __name__ == "__main__":
    sys.exit(main())

exception = Exception
syntaxerror = SyntaxError
