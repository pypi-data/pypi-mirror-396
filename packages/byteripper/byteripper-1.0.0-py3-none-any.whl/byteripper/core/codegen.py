import ast
import sys

def generate_code(node, indent=4):
    if sys.version_info >= (3, 9):
        try:
            return ast.unparse(node)
        except exception:
            pass
    generator = codegenerator(indent=indent)
    return generator.visit(node)

class codegenerator(ast.NodeVisitor):
    def __init__(self, indent=4):
        self.indent_size = indent
        self.indent_level = 0
        self.result = []

    def visit(self, node):
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        if isinstance(node, ast.expr):
            return self._expr_fallback(node)
        return ""

    def _expr_fallback(self, node):
        try:
            if sys.version_info >= (3, 9):
                return ast.unparse(node)
        except exception:
            pass
        return repr(node)

    def _indent(self):
        return " " * (self.indent_size * self.indent_level)

    def visit_module(self, node):
        lines = []
        for stmt in node.body:
            lines.append(self.visit(stmt))
        return "\n".join(lines)

    def visit_Module(self, node):
        return self.visit_module(node)

    def visit_expr(self, node):
        return f"{self._indent()}{self.visit(node.value)}"

    def visit_Expr(self, node):
        return self.visit_expr(node)

    def visit_assign(self, node):
        targets = ", ".join(self.visit(t) for t in node.targets)
        value = self.visit(node.value)
        return f"{self._indent()}{targets} = {value}"

    def visit_Assign(self, node):
        return self.visit_assign(node)

    def visit_augassign(self, node):
        target = self.visit(node.target)
        op = self._get_op_symbol(node.op)
        value = self.visit(node.value)
        return f"{self._indent()}{target} {op}= {value}"

    def visit_AugAssign(self, node):
        return self.visit_augassign(node)

    def visit_return(self, node):
        if node.value:
            return f"{self._indent()}return {self.visit(node.value)}"
        return f"{self._indent()}return"

    def visit_Return(self, node):
        return self.visit_return(node)

    def visit_import(self, node):
        names = ", ".join(self._format_alias(a) for a in node.names)
        return f"{self._indent()}import {names}"

    def visit_Import(self, node):
        return self.visit_import(node)

    def visit_importfrom(self, node):
        module = node.module or ""
        names = ", ".join(self._format_alias(a) for a in node.names)
        level = "." * node.level
        return f"{self._indent()}from {level}{module} import {names}"

    def visit_ImportFrom(self, node):
        return self.visit_importfrom(node)

    def _format_alias(self, alias):
        if alias.asname:
            return f"{alias.name} as {alias.asname}"
        return alias.name

    def visit_functiondef(self, node):
        decorators = ""
        for d in node.decorator_list:
            decorators += f"{self._indent()}@{self.visit(d)}\n"
        args = self._format_arguments(node.args)
        header = f"{self._indent()}def {node.name}({args}):"
        self.indent_level += 1
        body = "\n".join(self.visit(s) for s in node.body) or f"{self._indent()}pass"
        self.indent_level -= 1
        return f"{decorators}{header}\n{body}"

    def visit_FunctionDef(self, node):
        return self.visit_functiondef(node)

    def visit_asyncfunctiondef(self, node):
        decorators = ""
        for d in node.decorator_list:
            decorators += f"{self._indent()}@{self.visit(d)}\n"
        args = self._format_arguments(node.args)
        header = f"{self._indent()}async def {node.name}({args}):"
        self.indent_level += 1
        body = "\n".join(self.visit(s) for s in node.body) or f"{self._indent()}pass"
        self.indent_level -= 1
        return f"{decorators}{header}\n{body}"

    def visit_AsyncFunctionDef(self, node):
        return self.visit_asyncfunctiondef(node)

    def visit_classdef(self, node):
        decorators = ""
        for d in node.decorator_list:
            decorators += f"{self._indent()}@{self.visit(d)}\n"
        bases = ", ".join(self.visit(b) for b in node.bases)
        if bases:
            header = f"{self._indent()}class {node.name}({bases}):"
        else:
            header = f"{self._indent()}class {node.name}:"
        self.indent_level += 1
        body = "\n".join(self.visit(s) for s in node.body) or f"{self._indent()}pass"
        self.indent_level -= 1
        return f"{decorators}{header}\n{body}"

    def visit_ClassDef(self, node):
        return self.visit_classdef(node)

    def visit_if(self, node):
        test = self.visit(node.test)
        lines = [f"{self._indent()}if {test}:"]
        self.indent_level += 1
        for stmt in node.body:
            lines.append(self.visit(stmt))
        self.indent_level -= 1
        if node.orelse:
            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                lines.append(f"{self._indent()}el{self.visit(node.orelse[0]).lstrip()}")
            else:
                lines.append(f"{self._indent()}else:")
                self.indent_level += 1
                for stmt in node.orelse:
                    lines.append(self.visit(stmt))
                self.indent_level -= 1
        return "\n".join(lines)

    def visit_If(self, node):
        return self.visit_if(node)

    def visit_for(self, node):
        target = self.visit(node.target)
        iter_val = self.visit(node.iter)
        lines = [f"{self._indent()}for {target} in {iter_val}:"]
        self.indent_level += 1
        for stmt in node.body:
            lines.append(self.visit(stmt))
        self.indent_level -= 1
        if node.orelse:
            lines.append(f"{self._indent()}else:")
            self.indent_level += 1
            for stmt in node.orelse:
                lines.append(self.visit(stmt))
            self.indent_level -= 1
        return "\n".join(lines)

    def visit_For(self, node):
        return self.visit_for(node)

    def visit_while(self, node):
        test = self.visit(node.test)
        lines = [f"{self._indent()}while {test}:"]
        self.indent_level += 1
        for stmt in node.body:
            lines.append(self.visit(stmt))
        self.indent_level -= 1
        if node.orelse:
            lines.append(f"{self._indent()}else:")
            self.indent_level += 1
            for stmt in node.orelse:
                lines.append(self.visit(stmt))
            self.indent_level -= 1
        return "\n".join(lines)

    def visit_While(self, node):
        return self.visit_while(node)

    def visit_try(self, node):
        lines = [f"{self._indent()}try:"]
        self.indent_level += 1
        for stmt in node.body:
            lines.append(self.visit(stmt))
        self.indent_level -= 1
        for handler in node.handlers:
            lines.append(self.visit(handler))
        if node.orelse:
            lines.append(f"{self._indent()}else:")
            self.indent_level += 1
            for stmt in node.orelse:
                lines.append(self.visit(stmt))
            self.indent_level -= 1
        if node.finalbody:
            lines.append(f"{self._indent()}finally:")
            self.indent_level += 1
            for stmt in node.finalbody:
                lines.append(self.visit(stmt))
            self.indent_level -= 1
        return "\n".join(lines)

    def visit_Try(self, node):
        return self.visit_try(node)

    def visit_excepthandler(self, node):
        if node.type:
            type_str = self.visit(node.type)
            if node.name:
                header = f"{self._indent()}except {type_str} as {node.name}:"
            else:
                header = f"{self._indent()}except {type_str}:"
        else:
            header = f"{self._indent()}except:"
        lines = [header]
        self.indent_level += 1
        for stmt in node.body:
            lines.append(self.visit(stmt))
        self.indent_level -= 1
        return "\n".join(lines)

    def visit_ExceptHandler(self, node):
        return self.visit_excepthandler(node)

    def visit_with(self, node):
        items = ", ".join(self._format_withitem(i) for i in node.items)
        lines = [f"{self._indent()}with {items}:"]
        self.indent_level += 1
        for stmt in node.body:
            lines.append(self.visit(stmt))
        self.indent_level -= 1
        return "\n".join(lines)

    def visit_With(self, node):
        return self.visit_with(node)

    def _format_withitem(self, item):
        context = self.visit(item.context_expr)
        if item.optional_vars:
            var = self.visit(item.optional_vars)
            return f"{context} as {var}"
        return context

    def visit_raise(self, node):
        if node.exc:
            exc = self.visit(node.exc)
            if node.cause:
                cause = self.visit(node.cause)
                return f"{self._indent()}raise {exc} from {cause}"
            return f"{self._indent()}raise {exc}"
        return f"{self._indent()}raise"

    def visit_Raise(self, node):
        return self.visit_raise(node)

    def visit_pass(self, node):
        return f"{self._indent()}pass"

    def visit_Pass(self, node):
        return self.visit_pass(node)

    def visit_break(self, node):
        return f"{self._indent()}break"

    def visit_Break(self, node):
        return self.visit_break(node)

    def visit_continue(self, node):
        return f"{self._indent()}continue"

    def visit_Continue(self, node):
        return self.visit_continue(node)

    def visit_global(self, node):
        return f"{self._indent()}global {', '.join(node.names)}"

    def visit_Global(self, node):
        return self.visit_global(node)

    def visit_nonlocal(self, node):
        return f"{self._indent()}nonlocal {', '.join(node.names)}"

    def visit_Nonlocal(self, node):
        return self.visit_nonlocal(node)

    def visit_assert(self, node):
        test = self.visit(node.test)
        if node.msg:
            msg = self.visit(node.msg)
            return f"{self._indent()}assert {test}, {msg}"
        return f"{self._indent()}assert {test}"

    def visit_Assert(self, node):
        return self.visit_assert(node)

    def visit_delete(self, node):
        targets = ", ".join(self.visit(t) for t in node.targets)
        return f"{self._indent()}del {targets}"

    def visit_Delete(self, node):
        return self.visit_delete(node)

    def visit_binop(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = self._get_op_symbol(node.op)
        return f"({left} {op} {right})"

    def visit_BinOp(self, node):
        return self.visit_binop(node)

    def visit_unaryop(self, node):
        operand = self.visit(node.operand)
        op = self._get_unary_symbol(node.op)
        if op == "not ":
            return f"(not {operand})"
        return f"({op}{operand})"

    def visit_UnaryOp(self, node):
        return self.visit_unaryop(node)

    def visit_boolop(self, node):
        op = " and " if isinstance(node.op, ast.And) else " or "
        values = op.join(self.visit(v) for v in node.values)
        return f"({values})"

    def visit_BoolOp(self, node):
        return self.visit_boolop(node)

    def visit_compare(self, node):
        left = self.visit(node.left)
        parts = [left]
        for op, comp in zip(node.ops, node.comparators):
            parts.append(self._get_cmp_symbol(op))
            parts.append(self.visit(comp))
        return "(" + " ".join(parts) + ")"

    def visit_Compare(self, node):
        return self.visit_compare(node)

    def visit_call(self, node):
        func = self.visit(node.func)
        args = []
        for a in node.args:
            args.append(self.visit(a))
        for kw in node.keywords:
            if kw.arg:
                args.append(f"{kw.arg}={self.visit(kw.value)}")
            else:
                args.append(f"**{self.visit(kw.value)}")
        return f"{func}({', '.join(args)})"

    def visit_Call(self, node):
        return self.visit_call(node)

    def visit_name(self, node):
        return node.id

    def visit_Name(self, node):
        return self.visit_name(node)

    def visit_constant(self, node):
        return repr(node.value)

    def visit_Constant(self, node):
        return self.visit_constant(node)

    def visit_num(self, node):
        return repr(node.n)

    def visit_Num(self, node):
        return self.visit_num(node)

    def visit_str(self, node):
        return repr(node.s)

    def visit_Str(self, node):
        return self.visit_str(node)

    def visit_bytes(self, node):
        return repr(node.s)

    def visit_Bytes(self, node):
        return self.visit_bytes(node)

    def visit_nameconstant(self, node):
        return repr(node.value)

    def visit_NameConstant(self, node):
        return self.visit_nameconstant(node)

    def visit_list(self, node):
        elts = ", ".join(self.visit(e) for e in node.elts)
        return f"[{elts}]"

    def visit_List(self, node):
        return self.visit_list(node)

    def visit_tuple(self, node):
        elts = ", ".join(self.visit(e) for e in node.elts)
        if len(node.elts) == 1:
            return f"({elts},)"
        return f"({elts})"

    def visit_Tuple(self, node):
        return self.visit_tuple(node)

    def visit_set(self, node):
        elts = ", ".join(self.visit(e) for e in node.elts)
        return "{" + elts + "}"

    def visit_Set(self, node):
        return self.visit_set(node)

    def visit_dict(self, node):
        pairs = []
        for k, v in zip(node.keys, node.values):
            if k is None:
                pairs.append(f"**{self.visit(v)}")
            else:
                pairs.append(f"{self.visit(k)}: {self.visit(v)}")
        return "{" + ", ".join(pairs) + "}"

    def visit_Dict(self, node):
        return self.visit_dict(node)

    def visit_attribute(self, node):
        value = self.visit(node.value)
        return f"{value}.{node.attr}"

    def visit_Attribute(self, node):
        return self.visit_attribute(node)

    def visit_subscript(self, node):
        value = self.visit(node.value)
        slice_str = self.visit(node.slice)
        return f"{value}[{slice_str}]"

    def visit_Subscript(self, node):
        return self.visit_subscript(node)

    def visit_slice(self, node):
        lower = self.visit(node.lower) if node.lower else ""
        upper = self.visit(node.upper) if node.upper else ""
        step = self.visit(node.step) if node.step else ""
        if step:
            return f"{lower}:{upper}:{step}"
        return f"{lower}:{upper}"

    def visit_Slice(self, node):
        return self.visit_slice(node)

    def visit_index(self, node):
        return self.visit(node.value)

    def visit_Index(self, node):
        return self.visit_index(node)

    def visit_starred(self, node):
        return f"*{self.visit(node.value)}"

    def visit_Starred(self, node):
        return self.visit_starred(node)

    def visit_ifexp(self, node):
        body = self.visit(node.body)
        test = self.visit(node.test)
        orelse = self.visit(node.orelse)
        return f"({body} if {test} else {orelse})"

    def visit_IfExp(self, node):
        return self.visit_ifexp(node)

    def visit_lambda(self, node):
        args = self._format_arguments(node.args)
        body = self.visit(node.body)
        return f"(lambda {args}: {body})"

    def visit_Lambda(self, node):
        return self.visit_lambda(node)

    def visit_listcomp(self, node):
        elt = self.visit(node.elt)
        gens = " ".join(self._format_comprehension(g) for g in node.generators)
        return f"[{elt} {gens}]"

    def visit_ListComp(self, node):
        return self.visit_listcomp(node)

    def visit_setcomp(self, node):
        elt = self.visit(node.elt)
        gens = " ".join(self._format_comprehension(g) for g in node.generators)
        return "{" + f"{elt} {gens}" + "}"

    def visit_SetComp(self, node):
        return self.visit_setcomp(node)

    def visit_dictcomp(self, node):
        key = self.visit(node.key)
        value = self.visit(node.value)
        gens = " ".join(self._format_comprehension(g) for g in node.generators)
        return "{" + f"{key}: {value} {gens}" + "}"

    def visit_DictComp(self, node):
        return self.visit_dictcomp(node)

    def visit_generatorexp(self, node):
        elt = self.visit(node.elt)
        gens = " ".join(self._format_comprehension(g) for g in node.generators)
        return f"({elt} {gens})"

    def visit_GeneratorExp(self, node):
        return self.visit_generatorexp(node)

    def _format_comprehension(self, gen):
        target = self.visit(gen.target)
        iter_val = self.visit(gen.iter)
        result = f"for {target} in {iter_val}"
        for if_ in gen.ifs:
            result += f" if {self.visit(if_)}"
        return result

    def visit_await(self, node):
        return f"(await {self.visit(node.value)})"

    def visit_Await(self, node):
        return self.visit_await(node)

    def visit_yield(self, node):
        if node.value:
            return f"(yield {self.visit(node.value)})"
        return "(yield)"

    def visit_Yield(self, node):
        return self.visit_yield(node)

    def visit_yieldfrom(self, node):
        return f"(yield from {self.visit(node.value)})"

    def visit_YieldFrom(self, node):
        return self.visit_yieldfrom(node)

    def visit_formattedvalue(self, node):
        value = self.visit(node.value)
        return "{" + value + "}"

    def visit_FormattedValue(self, node):
        return self.visit_formattedvalue(node)

    def visit_joinedstr(self, node):
        parts = []
        for v in node.values:
            if isinstance(v, ast.Constant):
                parts.append(str(v.value))
            else:
                parts.append(self.visit(v))
        return 'f"' + "".join(parts) + '"'

    def visit_JoinedStr(self, node):
        return self.visit_joinedstr(node)

    def _format_arguments(self, args):
        parts = []
        defaults_offset = len(args.args) - len(args.defaults)
        for i, arg in enumerate(args.args):
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {self.visit(arg.annotation)}"
            default_idx = i - defaults_offset
            if default_idx >= 0:
                arg_str += f"={self.visit(args.defaults[default_idx])}"
            parts.append(arg_str)
        if args.vararg:
            parts.append(f"*{args.vararg.arg}")
        elif args.kwonlyargs:
            parts.append("*")
        for i, arg in enumerate(args.kwonlyargs):
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {self.visit(arg.annotation)}"
            if i < len(args.kw_defaults) and args.kw_defaults[i]:
                arg_str += f"={self.visit(args.kw_defaults[i])}"
            parts.append(arg_str)
        if args.kwarg:
            parts.append(f"**{args.kwarg.arg}")
        return ", ".join(parts)

    def _get_op_symbol(self, op):
        ops = {
            ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/",
            ast.FloorDiv: "//", ast.Mod: "%", ast.Pow: "**",
            ast.LShift: "<<", ast.RShift: ">>",
            ast.BitOr: "|", ast.BitXor: "^", ast.BitAnd: "&",
            ast.MatMult: "@",
        }
        return ops.get(type(op), "+")

    def _get_unary_symbol(self, op):
        ops = {
            ast.UAdd: "+", ast.USub: "-", ast.Not: "not ", ast.Invert: "~",
        }
        return ops.get(type(op), "+")

    def _get_cmp_symbol(self, op):
        ops = {
            ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<", ast.LtE: "<=",
            ast.Gt: ">", ast.GtE: ">=", ast.Is: "is", ast.IsNot: "is not",
            ast.In: "in", ast.NotIn: "not in",
        }
        return ops.get(type(op), "==")


exception = Exception
