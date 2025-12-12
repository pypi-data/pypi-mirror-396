import ast
import dis
import sys
from byteripper.core.opcodes import disassemble_bytecode

class astbuilder:
    def __init__(self, code_object, version_tuple=None):
        self.code = code_object
        self.version = version_tuple or sys.version_info[:3]
        self.instructions = []
        self.stack = []
        self.statements = []
        self.errors = []
        self.current_index = 0

    def build(self):
        try:
            self.instructions = disassemble_bytecode(self.code, self.version)
            self._process_instructions()
            module = ast.Module(body=self.statements, type_ignores=[])
            ast.fix_missing_locations(module)
            return module
        except exception as e:
            self.errors.append(f"ast build error: {str(e)}")
            return self._create_error_module()

    def _process_instructions(self):
        while self.current_index < len(self.instructions):
            try:
                self._process_instruction(self.instructions[self.current_index])
            except exception as e:
                self.errors.append(f"error at offset {self.instructions[self.current_index]['offset']}: {str(e)}")
            self.current_index += 1
        self._finalize()

    def _process_instruction(self, instr):
        opname = instr["opname"]
        arg = instr["arg"]
        handler = getattr(self, f"_op_{opname.lower()}", None)
        if handler:
            handler(arg)
        elif opname.startswith("unary_"):
            self._handle_unary(opname)
        elif opname.startswith("binary_"):
            self._handle_binary(opname)
        elif opname.startswith("inplace_"):
            self._handle_inplace(opname)

    def _op_load_const(self, arg):
        if arg is not None and arg < len(self.code.co_consts):
            value = self.code.co_consts[arg]
            self.stack.append(self._make_const(value))

    def _op_load_name(self, arg):
        if arg is not None and arg < len(self.code.co_names):
            name = self.code.co_names[arg]
            self.stack.append(ast.Name(id=name, ctx=ast.Load()))

    def _op_load_fast(self, arg):
        if arg is not None and arg < len(self.code.co_varnames):
            name = self.code.co_varnames[arg]
            self.stack.append(ast.Name(id=name, ctx=ast.Load()))

    def _op_load_global(self, arg):
        if arg is not None and arg < len(self.code.co_names):
            name = self.code.co_names[arg]
            self.stack.append(ast.Name(id=name, ctx=ast.Load()))

    def _op_store_name(self, arg):
        if arg is not None and arg < len(self.code.co_names):
            name = self.code.co_names[arg]
            if self.stack:
                value = self.stack.pop()
                target = ast.Name(id=name, ctx=ast.Store())
                self.statements.append(ast.Assign(targets=[target], value=value))

    def _op_store_fast(self, arg):
        if arg is not None and arg < len(self.code.co_varnames):
            name = self.code.co_varnames[arg]
            if self.stack:
                value = self.stack.pop()
                target = ast.Name(id=name, ctx=ast.Store())
                self.statements.append(ast.Assign(targets=[target], value=value))

    def _op_store_global(self, arg):
        if arg is not None and arg < len(self.code.co_names):
            name = self.code.co_names[arg]
            if self.stack:
                value = self.stack.pop()
                target = ast.Name(id=name, ctx=ast.Store())
                self.statements.append(ast.Assign(targets=[target], value=value))

    def _op_return_value(self, arg):
        if self.stack:
            value = self.stack.pop()
            self.statements.append(ast.Return(value=value))
        else:
            self.statements.append(ast.Return(value=None))

    def _op_pop_top(self, arg):
        if self.stack:
            expr = self.stack.pop()
            if not isinstance(expr, ast.expr):
                expr = self._make_const(expr)
            self.statements.append(ast.Expr(value=expr))

    def _op_call_function(self, arg):
        if arg is not None and len(self.stack) >= arg + 1:
            args = []
            for _ in range(arg):
                args.insert(0, self.stack.pop())
            func = self.stack.pop()
            call = ast.Call(func=func, args=args, keywords=[])
            self.stack.append(call)

    def _op_call(self, arg):
        self._op_call_function(arg)

    def _op_build_list(self, arg):
        if arg is not None and len(self.stack) >= arg:
            elements = []
            for _ in range(arg):
                elements.insert(0, self.stack.pop())
            self.stack.append(ast.List(elts=elements, ctx=ast.Load()))

    def _op_build_tuple(self, arg):
        if arg is not None and len(self.stack) >= arg:
            elements = []
            for _ in range(arg):
                elements.insert(0, self.stack.pop())
            self.stack.append(ast.Tuple(elts=elements, ctx=ast.Load()))

    def _op_build_set(self, arg):
        if arg is not None and len(self.stack) >= arg:
            elements = []
            for _ in range(arg):
                elements.insert(0, self.stack.pop())
            self.stack.append(ast.Set(elts=elements))

    def _op_build_map(self, arg):
        if arg is not None and len(self.stack) >= arg * 2:
            keys = []
            values = []
            for _ in range(arg):
                values.insert(0, self.stack.pop())
                keys.insert(0, self.stack.pop())
            self.stack.append(ast.Dict(keys=keys, values=values))

    def _op_import_name(self, arg):
        if arg is not None and arg < len(self.code.co_names):
            name = self.code.co_names[arg]
            if len(self.stack) >= 2:
                self.stack.pop()
                self.stack.pop()
            self.stack.append(ast.Name(id=name, ctx=ast.Load()))
            imp = ast.Import(names=[ast.alias(name=name, asname=None)])
            self.statements.append(imp)

    def _op_import_from(self, arg):
        if arg is not None and arg < len(self.code.co_names):
            name = self.code.co_names[arg]
            self.stack.append(ast.Name(id=name, ctx=ast.Load()))

    def _op_load_attr(self, arg):
        if arg is not None and arg < len(self.code.co_names) and self.stack:
            attr = self.code.co_names[arg]
            value = self.stack.pop()
            self.stack.append(ast.Attribute(value=value, attr=attr, ctx=ast.Load()))

    def _op_store_attr(self, arg):
        if arg is not None and arg < len(self.code.co_names) and len(self.stack) >= 2:
            attr = self.code.co_names[arg]
            obj = self.stack.pop()
            value = self.stack.pop()
            target = ast.Attribute(value=obj, attr=attr, ctx=ast.Store())
            self.statements.append(ast.Assign(targets=[target], value=value))

    def _op_binary_subscr(self, arg):
        if len(self.stack) >= 2:
            index = self.stack.pop()
            value = self.stack.pop()
            self.stack.append(ast.Subscript(value=value, slice=index, ctx=ast.Load()))

    def _op_store_subscr(self, arg):
        if len(self.stack) >= 3:
            index = self.stack.pop()
            obj = self.stack.pop()
            value = self.stack.pop()
            target = ast.Subscript(value=obj, slice=index, ctx=ast.Store())
            self.statements.append(ast.Assign(targets=[target], value=value))

    def _handle_binary(self, opname):
        if len(self.stack) >= 2:
            right = self.stack.pop()
            left = self.stack.pop()
            op_map = {
                "binary_add": ast.Add(),
                "binary_subtract": ast.Sub(),
                "binary_multiply": ast.Mult(),
                "binary_true_divide": ast.Div(),
                "binary_floor_divide": ast.FloorDiv(),
                "binary_modulo": ast.Mod(),
                "binary_power": ast.Pow(),
                "binary_lshift": ast.LShift(),
                "binary_rshift": ast.RShift(),
                "binary_and": ast.BitAnd(),
                "binary_or": ast.BitOr(),
                "binary_xor": ast.BitXor(),
                "binary_matrix_multiply": ast.MatMult(),
            }
            op = op_map.get(opname.lower(), ast.Add())
            self.stack.append(ast.BinOp(left=left, op=op, right=right))

    def _handle_unary(self, opname):
        if self.stack:
            operand = self.stack.pop()
            op_map = {
                "unary_positive": ast.UAdd(),
                "unary_negative": ast.USub(),
                "unary_not": ast.Not(),
                "unary_invert": ast.Invert(),
            }
            op = op_map.get(opname.lower(), ast.UAdd())
            self.stack.append(ast.UnaryOp(op=op, operand=operand))

    def _handle_inplace(self, opname):
        if len(self.stack) >= 2:
            right = self.stack.pop()
            left = self.stack.pop()
            op_map = {
                "inplace_add": ast.Add(),
                "inplace_subtract": ast.Sub(),
                "inplace_multiply": ast.Mult(),
                "inplace_true_divide": ast.Div(),
                "inplace_floor_divide": ast.FloorDiv(),
                "inplace_modulo": ast.Mod(),
                "inplace_power": ast.Pow(),
            }
            op = op_map.get(opname.lower(), ast.Add())
            result = ast.BinOp(left=left, op=op, right=right)
            if isinstance(left, ast.Name):
                target = ast.Name(id=left.id, ctx=ast.Store())
                self.statements.append(ast.Assign(targets=[target], value=result))
            else:
                self.stack.append(result)

    def _op_compare_op(self, arg):
        if len(self.stack) >= 2:
            right = self.stack.pop()
            left = self.stack.pop()
            cmp_ops = [
                ast.Lt(), ast.LtE(), ast.Eq(), ast.NotEq(),
                ast.Gt(), ast.GtE(), ast.In(), ast.NotIn(),
                ast.Is(), ast.IsNot(),
            ]
            op = cmp_ops[arg] if arg < len(cmp_ops) else ast.Eq()
            self.stack.append(ast.Compare(left=left, ops=[op], comparators=[right]))

    def _op_jump_if_true_or_pop(self, arg):
        pass

    def _op_jump_if_false_or_pop(self, arg):
        pass

    def _op_jump_forward(self, arg):
        pass

    def _op_jump_absolute(self, arg):
        pass

    def _op_pop_jump_if_true(self, arg):
        pass

    def _op_pop_jump_if_false(self, arg):
        pass

    def _op_for_iter(self, arg):
        pass

    def _op_get_iter(self, arg):
        pass

    def _op_setup_loop(self, arg):
        pass

    def _op_resume(self, arg):
        pass

    def _op_push_null(self, arg):
        self.stack.append(ast.Constant(value=None))

    def _op_precall(self, arg):
        pass

    def _op_make_function(self, arg):
        if len(self.stack) >= 2:
            name_const = self.stack.pop()
            code_const = self.stack.pop()
            if isinstance(name_const, ast.Constant):
                func_name = name_const.value
            else:
                func_name = "unknown_func"
            func_def = ast.FunctionDef(
                name=str(func_name),
                args=ast.arguments(
                    posonlyargs=[],
                    args=[],
                    vararg=None,
                    kwonlyargs=[],
                    kw_defaults=[],
                    kwarg=None,
                    defaults=[]
                ),
                body=[ast.Pass()],
                decorator_list=[],
                returns=None
            )
            self.stack.append(ast.Name(id=str(func_name), ctx=ast.Load()))

    def _op_load_build_class(self, arg):
        self.stack.append(ast.Name(id="__build_class__", ctx=ast.Load()))

    def _op_copy(self, arg):
        if self.stack:
            self.stack.append(self.stack[-1])

    def _op_swap(self, arg):
        if len(self.stack) >= 2:
            self.stack[-1], self.stack[-2] = self.stack[-2], self.stack[-1]

    def _op_cache(self, arg):
        pass

    def _op_binary_op(self, arg):
        if len(self.stack) >= 2:
            right = self.stack.pop()
            left = self.stack.pop()
            ops = [
                ast.Add(), ast.And(), ast.FloorDiv(), ast.LShift(),
                ast.MatMult(), ast.Mult(), ast.Mod(), ast.Or(),
                ast.Pow(), ast.RShift(), ast.Sub(), ast.Div(),
                ast.BitXor(), ast.BitAnd(), ast.BitOr()
            ]
            op = ops[arg % len(ops)] if arg is not None else ast.Add()
            self.stack.append(ast.BinOp(left=left, op=op, right=right))

    def _op_kw_names(self, arg):
        pass

    def _make_const(self, value):
        import types
        if value is None:
            return ast.Constant(value=None)
        if isinstance(value, bool):
            return ast.Constant(value=value)
        if isinstance(value, (int, float, complex)):
            return ast.Constant(value=value)
        if isinstance(value, str):
            return ast.Constant(value=value)
        if isinstance(value, bytes):
            return ast.Constant(value=value)
        if isinstance(value, types.CodeType):
            return ast.Constant(value=None)
        if isinstance(value, tuple):
            filtered = [v for v in value if not isinstance(v, types.CodeType)]
            return ast.Tuple(elts=[self._make_const(v) for v in filtered], ctx=ast.Load())
        if isinstance(value, list):
            return ast.List(elts=[self._make_const(v) for v in value], ctx=ast.Load())
        if isinstance(value, dict):
            keys = [self._make_const(k) for k in value.keys()]
            vals = [self._make_const(v) for v in value.values()]
            return ast.Dict(keys=keys, values=vals)
        if isinstance(value, set):
            return ast.Set(elts=[self._make_const(v) for v in value])
        if isinstance(value, frozenset):
            return ast.Set(elts=[self._make_const(v) for v in value])
        try:
            return ast.Constant(value=repr(value))
        except exception:
            return ast.Constant(value=None)

    def _finalize(self):
        while self.stack:
            expr = self.stack.pop()
            if isinstance(expr, ast.expr):
                self.statements.append(ast.Expr(value=expr))

    def _create_error_module(self):
        error_comment = ast.Expr(value=ast.Constant(value="decompilation error"))
        return ast.Module(body=[error_comment], type_ignores=[])


def build_ast(code_object, version_tuple=None):
    builder = astbuilder(code_object, version_tuple)
    return builder.build(), builder.errors


exception = Exception
