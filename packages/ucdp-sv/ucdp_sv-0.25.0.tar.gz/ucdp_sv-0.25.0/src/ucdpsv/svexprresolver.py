#
# MIT License
#
# Copyright (c) 2024-2025 nbiotcloud
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

"""SystemVerilog Expression Resolver."""

from collections.abc import Iterable, Iterator
from typing import ClassVar, Literal, TypeAlias

import ucdp as u
from aligntext import Align
from matchor import matchs
from ucdp.ifdef import Ifdefs

DIRKEYWORDS = {
    u.IN: "input",
    u.OUT: "output",
    u.INOUT: "inout",
}
DIRCOMMENT = {
    u.IN: "I",
    u.OUT: "O",
    u.INOUT: "IO",
}

SvDecl = tuple[str, str]


def _is_param(ident: u.Ident) -> bool:
    return isinstance(ident, u.Param)


def _is_const(ident: u.Ident) -> bool:
    return isinstance(ident, u.Const)


LevelIter: TypeAlias = Iterator[tuple[int | None, u.Ident | u.Assign]]


class SvExprResolver(u.ExprResolver):
    """
    SystemVerilog Expression Resolver.

    This Expression Resolver Converts the UCDP internal expression representation
    into SystemVerilog.

    !!! example

            >>> import ucdp as u
            >>> import ucdpsv as usv
            >>> resolver = usv.SvExprResolver()
            >>> resolver.resolve(u.ConstExpr(u.UintType(18, default=5)))
            "18'h00005"
            >>> resolver.resolve(u.ConstExpr(u.SintType(18, default=-5)))
            "18'sh3FFFB"
    """

    ff_dly: str = ""
    _opremap: ClassVar[dict[str, str]] = {"//": "/"}

    @staticmethod
    def _get_rail_value(value: int) -> str:
        return f"1'b{value}"

    @staticmethod
    def _get_bit_value(value: int) -> str:
        return f"1'b{value}"

    def _get_uint_value(self, value: int, width: int | u.Expr) -> str:
        if isinstance(width, int):
            hexstr = f"{value:X}".zfill((width + 3) // 4)
            return f"{width}'h{hexstr}"

        # parameterized width
        width = self.resolve(width)
        if value != 0:
            return f"'d{value}"

        return f"{{{width} {{1'b0}}}}"

    def _get_sint_value(self, value: int, width: int | u.Expr) -> str:
        if isinstance(width, int):
            wrap = 1 << width
            value = (value + wrap) % wrap
            hexstr = f"{value:X}".zfill((width + 3) // 4)
            return f"{width}'sh{hexstr}"

        # parameterized width
        width = self.resolve(width)

        # This is not the best, but all we can do - or?
        if value > 0:
            return f"'d{value}"
        if value < 0:
            return f"-('d{-value})"

        return f"{{{width} {{1'sb0}}}}"

    @staticmethod
    def _get_integer_value(value: int) -> str:
        return str(value)

    @staticmethod
    def _get_bool_value(value: bool) -> str:
        if value:
            return "true"
        return "false"

    @staticmethod
    def _get_string_value(value) -> str:
        return f'"{value}"'

    def _resolve_log2expr(self, expr: u.Log2Expr) -> str:
        return f"$clog2({self.resolve(expr.expr)})"

    def get_paramdecls(self, idents: u.Idents, is_last: bool = True, indent: int = 0) -> Align:
        """Return `Align` With Parameter Declarations."""
        return self._get_paramdecls(idents.leveliter(filter_=_is_param), "parameter", ",", is_last, indent)

    def get_localparamdecls(self, idents: u.Idents, indent: int = 0) -> Align:
        """Return `Align` With Local Parameter Declarations."""
        return self._get_paramdecls(idents.leveliter(filter_=_is_const), "localparam", ";", False, indent)

    def _get_paramdecls(self, leveliter: LevelIter, keyword: str, sep: str, is_last: bool, indent: int) -> Align:
        align = Align(rtrim=True, strip_empty_cols=True)
        pre = " " * indent
        align.set_separators(" ", first=pre)
        for ident, svdecl, svsep in self._iter_idents(align, pre, leveliter, sep, is_last):
            name = ident.name
            svdims = self.get_dims(ident.type_)
            svdefault = self.get_default(ident.type_)
            svcomment = _get_comment(ident.doc.comment_or_title)
            svdefault = f"{svdefault}{svsep}"
            align.add_row((keyword, *svdecl, name, svdims, "=", svdefault, svcomment))
        return align

    def get_portdecls(
        self,
        ports: u.Idents,
        is_last: bool = True,
        indent: int = 0,
        wirenames: u.Names | None = None,
        no_comments: bool = False,
    ) -> Align:
        """Return `Align` With Port Declarations."""
        return self._get_signaldecls(
            ports.leveliter(),
            ",",
            is_last=is_last,
            indent=indent,
            wirenames=wirenames,
            ports=True,
            no_comments=no_comments,
        )

    def get_signaldecls(self, signals: u.Idents, indent: int = 0, wirenames: u.Names | None = None) -> Align:
        """Return `Align` With Signal Declarations."""

        def stop(signal):
            return isinstance(signal, u.Port)

        return self._get_signaldecls(
            signals.leveliter(stop=stop), ";", is_last=False, indent=indent, wirenames=wirenames
        )

    def _get_signaldecls(
        self,
        leveliter: LevelIter,
        sep: str,
        is_last: bool,
        indent: int,
        wirenames: u.Names | None = None,
        ports: bool = False,
        no_comments: bool = False,
    ) -> Align:
        align = Align(rtrim=True, strip_empty_cols=True)
        pre = " " * indent
        align.set_separators(" ", first=pre)
        wirenames = u.split(wirenames)
        for ident, svdecl, svsep in self._iter_idents(align, pre, leveliter, sep, is_last, no_comments=no_comments):
            name = ident.name
            svdims = self.get_dims(ident.type_)
            if svdims:
                svdims = f"{svdims}{svsep}"
            else:
                name = f"{name}{svsep}"
            comments = [ident.doc.comment_or_title]
            try:
                clkrel = ident.clkrel
                if clkrel:
                    comments.insert(0, clkrel.info)
            except AttributeError:
                pass
            svcomment = _get_comment(u.join_names(*comments, concat=" - "))
            if ports:
                align.add_row((*_get_port_decl(ident, svdecl), name, svdims, svcomment))
            else:
                align.add_row((*svdecl, name, svdims, svcomment))
        return align

    def get_instparams(self, mod: u.BaseMod, is_last: bool = True, indent: int = 0) -> Align:
        """Return `Align` With Parameter Declarations."""
        align = Align(rtrim=True)
        pre = " " * indent
        align.set_separators("(", ")", "", first=pre)

        def filter_(ident):
            return isinstance(ident, u.Param) and ident.value is not None

        leveliter: LevelIter = ((None, ident) for ident in mod.namespace.iter(filter_=filter_))
        for ident, _, svsep in self._iter_idents(align, pre, leveliter, ",", is_last):
            name = f".{ident.name}"
            expr = self.get_value(ident)
            svcomment = _get_comment(ident.doc.comment_or_title, pre=" ")
            align.add_row(name, expr, svsep, svcomment)
        return align

    def get_instcons(
        self, instcons: u.Assigns, skips: u.Names | None = None, is_last: bool = True, indent: int = 0
    ) -> Align:
        """Return `Align` With Parameter Declarations."""
        align = Align(rtrim=True)
        pre = " " * indent
        align.set_separators("(", ")", "", first=pre)
        skips = u.split(skips)
        if skips:
            instconstiter = (
                (None, inst) for inst in instcons.iter(filter_=lambda ident: not matchs(ident.name, skips))
            )
        else:
            instconstiter = ((None, inst) for inst in instcons.iter())

        for assign, _, svsep in self._iter_idents(align, pre, instconstiter, ",", is_last):
            target = assign.target
            comments = []
            if target.suffix != target.direction.suffix:
                comments.append(DIRCOMMENT[target.direction])
            if isinstance(target.type_, u.RailType):
                comments.append("RAIL")

            source = assign.source
            if source is None:
                source = u.TODO

            if isinstance(source, u.Default):
                comments.append(source.note)
                if target.direction == u.IN:
                    source = self.get_default(target.type_)
                else:
                    source = ""
            elif isinstance(source, u.Note):
                source = f"/* {source.note} */"
            else:
                source = self.resolve(source)
            if target.clkrel:
                comments.append(target.clkrel.info)
            comments.append(target.doc.comment_or_title)
            svcomment = _get_comment(u.join_names(*comments, concat=" - "), pre=" ")
            align.add_row(f".{assign.name}", source, svsep, svcomment)
        return align

    def get_defaults(self, assigns: Iterable[u.Assign], indent: int = 0, oper: str = "=") -> Align:
        """Get Assigns."""
        align = Align(rtrim=True, strip_empty_cols=True)
        pre = " " * indent
        align.set_separators(" ", first=pre)
        levelassigns: LevelIter = ((0, assign) for assign in assigns)
        for ident, _, _ in self._iter_idents(align, pre, levelassigns):
            svvalue = self.get_value(ident)
            align.add_row((ident.name, f"{oper} {svvalue};"))
        return align

    def get_assigns(self, assigns: u.Assigns, indent: int, oper: str = "") -> Align:  # noqa: C901
        """Get Systemverilog Continuous Assigns."""
        align = Align(rtrim=True, strip_empty_cols=True)
        pre = " " * indent
        align.set_separators(" ", first=pre)
        levelassigns: LevelIter = ((None, assign) for assign in assigns)
        if oper:
            for assign, _, _ in self._iter_idents(align, pre, levelassigns):
                name = assign.target.name
                source = assign.source
                if source is not None:
                    source = self.resolve(source)
                if source is None:
                    source = self.get_value(assign.target)
                direction = assign.target.direction
                if direction in (u.OUT, u.FWD):
                    align.add_row((name, oper, f"{source};"))
                elif direction in (u.IN, u.BWD):
                    align.add_row((source, oper, f"{name};"))
        else:
            for assign, _, _ in self._iter_idents(align, pre, levelassigns):
                name = assign.target.name
                source = assign.source
                if source is not None:
                    source = self.resolve(source)
                direction = assign.target.direction
                if direction in (u.OUT, u.FWD):
                    align.add_row(("assign", "", name, "=", f"{source};"))
                elif direction in (u.IN, u.BWD):
                    align.add_row(("assign", "", source, "=", f"{name};"))
                else:
                    align.add_row(("tran", f"u_tran_{name}", f"({name},", "", f"{source});"))
        return align

    def get_decl(self, type_: u.BaseType) -> SvDecl | None:  # noqa: C901, PLR0911, PLR0912
        """Get SV Declaration."""
        dims = []
        while isinstance(type_, u.ArrayType):
            if type_.packed:
                dims.append(self._resolve_slice(type_.slice_).replace(" ", ""))
            type_ = type_.itemtype

        while isinstance(type_, u.BaseEnumType):
            type_ = type_.keytype

        if isinstance(type_, u.RailType):
            return "wire", "".join(dims)
        if isinstance(type_, u.BitType):
            keyword = "logic" if type_.logic else "bit"
            return keyword, "".join(dims)
        if isinstance(type_, u.UintType):
            keyword = "logic" if type_.logic else "bit"
            dims.insert(0, self._resolve_slice(type_.slice_).replace(" ", ""))
            return keyword, "".join(dims)

        if isinstance(type_, u.SintType):
            keyword = "logic signed" if type_.logic else "bit signed"
            dims.insert(0, self._resolve_slice(type_.slice_).replace(" ", ""))
            return keyword, "".join(dims)

        if isinstance(type_, u.BaseStructType):
            return None

        if isinstance(type_, u.IntegerType):
            keyword = "integer" if type_.logic else "int"
            return keyword, "".join(dims)

        if isinstance(type_, u.BoolType):
            return "bool", "".join(dims)

        if isinstance(type_, u.StringType):
            return "string", "".join(dims)

        if isinstance(type_, u.FloatType):
            return "real", "".join(dims)

        if isinstance(type_, u.DoubleType):
            return "real", "".join(dims)

        raise ValueError(type_)  # pragma: no cover

    def get_dims(self, type_: u.BaseType) -> str:
        """Get SV Dimensions."""
        dims = []
        while isinstance(type_, u.ArrayType) and not type_.packed:
            dims.append(self._resolve_slice(type_.slice_).replace(" ", ""))
            type_ = type_.itemtype
        return "".join(dims)

    def get_default(self, type_: u.BaseType) -> str:
        """Get SV Default."""
        return self._resolve_value(type_)

    def get_value(self, ident: u.Ident) -> str:
        """Get SV Value."""
        return self._resolve_value(ident.type_, value=getattr(ident, "value", None))

    @staticmethod
    def _get_define(define: u.Define) -> str:
        return f"`{define.name[1:]}"

    def _iter_idents(
        self,
        align: Align,
        pre: str,
        leveliter: LevelIter,
        sep: str = ";",
        is_last: bool = False,
        no_comments: bool = False,
    ) -> Iterator[tuple[u.Ident, SvDecl, str]]:
        decls = [(level, ident, self.get_decl(ident.type_)) for level, ident in leveliter]
        endmap = _get_endmap(decls) if is_last else set()
        pendlevel: int | None = None
        ifdefstack: list[str] = []
        ended = False
        # Iterate over all identifier and their declarations
        for level, ident, svdecl in decls:
            # emit ifdef, even if empty
            _add_ifdef(pre, align, ifdefstack, ident.ifdefs)
            if svdecl is not None:
                if ended:
                    align.add_spacer(f"{pre}{sep}")
                    ended = False
                if not no_comments:
                    pendlevel = _add_declcomment(align, level, ident, pendlevel, svdecl, pre)
                if ident.name in endmap:
                    yield ident, svdecl, ""
                    ended = True
                else:
                    yield ident, svdecl, sep
            elif not no_comments:
                pendlevel = _add_declcomment(align, level, ident, pendlevel, svdecl, pre)
        _add_ifdef(pre, align, ifdefstack)

    def get_ident_expr(self, type_: u.BaseScalarType, name: str, op: Literal[0, 1, "", "~"] | None) -> str | None:
        """Get Ident Expression."""
        if op is None:
            return None
        if op == 0:
            return self._resolve_value(type_, value=0)
        if op == 1:
            return self._resolve_value(type_, value=type_.max_)
        return f"{op}{name}"

    def _get_array_value(self, itemvalue: str, slice_: u.Slice) -> str:
        width = slice_.width
        if not isinstance(width, int):
            width = self._resolve(width)
        return f"'{{{width}{{{itemvalue}}}}}"

    def split_mux_conds(self, sel, conds):
        """Split Multiplexer Conditions."""
        cases, defaultcase = [], None
        default = sel.type_.default

        for cond, assigns in conds.items():
            condstr = self._resolve(cond)
            is_range = isinstance(cond, u.RangeExpr)
            try:
                is_default = default in cond.range_ if is_range else default == sel.type_.encode(cond)
            except ValueError:
                is_default = False
            if is_default:
                defaultcase = condstr, assigns
            elif is_range:
                cases.append((condstr, assigns))
            else:
                cases.append((condstr, assigns))

        return cases, defaultcase


def _get_comment(comment, level=0, pre="") -> str:
    """Return Systemverilog Comment."""
    if comment:
        comment = comment.split("\n", maxsplit=1)[0]
        fill = "  " * level
        return f"{pre}// {fill}{comment}"
    return ""


def _get_endmap(decls: Iterable[tuple[int, u.Ident, SvDecl | None]]) -> set[str]:
    """Create Auxiliary Structure To Determine Proper Commas."""
    endmap: set[str] = set()
    for _, ident, svdecl in decls:
        if svdecl is not None:
            if not ident.ifdefs:
                endmap.clear()
            endmap.add(ident.name)
    return endmap


def _add_ifdef(pre: str, align: Align, stack: list[str], ifdefs: Ifdefs = ()) -> None:
    """Add IFDEF/ENDIFs."""
    stackset = set(stack)
    ifdefset = set(ifdefs)
    if stackset == ifdefset:  # fit - nothing to do
        return

    # remove from right, until all obsolete defines are gone
    obsolete = stackset - ifdefset
    if obsolete:
        for ifdef in reversed(tuple(stack)):
            stack.remove(ifdef)
            obsolete.discard(ifdef)
            indent = "  " * len(stack)
            align.add_spacer(f"{pre}{indent}`endif // {ifdef}")
            if not obsolete:
                break

    # add missing
    for ifdef in ifdefs:
        if ifdef not in stack:
            indent = "  " * len(stack)
            if ifdef.startswith("!"):
                # ifndef
                stack.append(ifdef)
                align.add_spacer(f"{pre}{indent}`ifndef {ifdef[1:]}")
            else:
                # ifdef
                stack.append(ifdef)
                align.add_spacer(f"{pre}{indent}`ifdef {ifdef}")


def _add_declcomment(align: Align, level: int | None, ident: u.Ident | u.Assign, pendlevel: int | None, svdecl, pre):
    """Add Struct Declaration Comments ."""
    if level is None:
        return None
    if svdecl is None:
        name = ident.name
        comment = ident.doc.comment_or_title or ""
        if name and comment:
            comment = f"{name}: {comment}"
        else:
            comment = f"{name}{comment}"
        if comment:
            align.add_spacer(_get_comment(comment, level=level, pre=pre))
            return level
    if pendlevel is not None and pendlevel >= level:
        align.add_spacer(_get_comment("-", level=pendlevel, pre=pre))
        return None
    return pendlevel


def _get_port_decl(ident: u.Ident, svdecl: SvDecl) -> tuple[str, str, str]:
    dirkeyword = DIRKEYWORDS[ident.direction]
    svdecl0 = svdecl[0].replace("logic", "wire") if ident.direction != u.OUT else svdecl[0]
    return dirkeyword, svdecl0, svdecl[1]


def get_resolver(mod: u.BaseMod, inst: u.BaseMod | None = None) -> SvExprResolver:
    """Get SvExprResolver for `mod`."""
    if inst is not None:
        return SvExprResolver(namespace=mod.namespace, remap=inst.params + inst.consts)
    return SvExprResolver(namespace=mod.namespace)
