from __future__ import annotations

import ast as py_ast

import attr
from enum import Enum, auto
from typing import Optional, Any, List, Dict, Union


@attr.s(auto_attribs=True)
class Span:
    start_line: int
    start_column: int
    end_line: int
    end_column: int

    @staticmethod
    def from_ast(node: py_ast.AST) -> Span:
        end_lineno = node.end_lineno if node.end_lineno is not None else node.lineno + 1
        end_col_offset = (
            node.end_col_offset + 1
            if node.end_col_offset is not None
            else node.col_offset + 2
        )
        return Span(node.lineno, node.col_offset + 1, end_lineno, end_col_offset)

    def merge(self, span: Span) -> Span:
        self_start = (self.start_line, self.start_column)
        span_start = (span.start_line, span.start_column)
        start_line, start_col = min(self_start, span_start)

        self_end = (self.end_line, self.end_column)
        span_end = (span.end_line, span.end_column)
        end_line, end_col = max(self_end, span_end)

        return Span(start_line, start_col, end_line, end_col)

    def between(self, span: Span) -> Span:
        """The span between two spans"""
        return Span(self.end_line, self.end_column, span.start_line, span.start_column)

    def subtract(self, span: Span) -> Span:
        return Span(self.start_line, self.start_column, span.start_line, span.start_column)

    @staticmethod
    def invalid() -> Span:
        return Span(-1, -1, -1, -1)


@attr.s(auto_attribs=True)
class Id:
    names: List[str]

    @staticmethod
    def from_str(s: str) -> Id:
        """Parse and Id from a `.` separated string."""
        return Id(s.split("."))

    @staticmethod
    def invalid() -> Id:
        return Id([])

    @property
    def full_name(self) -> str:
        """A `.` seperated string of the fully qualified Id"""
        return ".".join(self.names)

    @property
    def base_name(self) -> str:
        """Unqualified name of the Id"""
        return self.names[-1]


Name = str


@attr.s(auto_attribs=True)
class Node:
    span: Span


@attr.s(auto_attribs=True)
class Parameter(Node):
    name: Name
    ty: Optional[Type]


class Type(Node):
    pass


class Stmt(Node):
    pass


class Expr(Node):
    pass


@attr.s(auto_attribs=True)
class Module(Node):
    funcs: Dict[Name, Union[Class, Function]]


@attr.s(auto_attribs=True)
class Var(Expr):
    name: Id

    @staticmethod
    def invalid() -> Var:
        return Var(Span.invalid(), name.invalid())


class BuiltinOp(Enum):
    Add = auto()
    Sub = auto()
    Mul = auto()
    Div = auto()
    FloorDiv = auto()
    Mod = auto()
    SubScript = auto()
    And = auto()
    Or = auto()
    Eq = auto()
    GT = auto()
    GE = auto()
    LT = auto()
    LE = auto()
    Not = auto()


@attr.s(auto_attribs=True)
class Op(Node):
    name: BuiltinOp


@attr.s(auto_attribs=True)
class Constant(Expr):
    value: Union[float, int]


@attr.s(auto_attribs=True)
class Call(Expr):
    name: Union[Var, Op]
    params: List[Expr]


@attr.s(auto_attribs=True)
class Return(Stmt):
    value: Optional[Expr]


@attr.s(auto_attribs=True)
class Assign(Stmt):
    lhs: Var
    rhs: Expr


@attr.s(auto_attribs=True)
class Function(Node):
    name: Name
    params: List[Parameter]
    ret_type: Type
    body: Block


@attr.s(auto_attribs=True)
class Block(Node):
    stmts: List[Stmt]


@attr.s(auto_attribs=True)
class For(Stmt):
    lhs: Var
    rhs: Expr
    body: Block


@attr.s(auto_attribs=True)
class With(Stmt):
    lhs: Expr
    rhs: Var
    body: Block


@attr.s(auto_attribs=True)
class Class(Node):
    funcs: Dict[Name, Function]
