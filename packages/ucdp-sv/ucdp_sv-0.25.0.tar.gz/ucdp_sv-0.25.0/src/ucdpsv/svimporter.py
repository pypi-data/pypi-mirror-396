#
# MIT License
#
# Copyright (c) 2025 nbiotcloud
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

"""SystemVerilog Importer."""

# ruff: noqa: PLW2901

import re
from pathlib import Path
from typing import Any, TypeAlias

import hdl_parser as hdl
import ucdp as u
from matchor import match

Attrs: TypeAlias = dict[str, Any]
AttrsDict: TypeAlias = dict[str, Attrs]
AttrsList: TypeAlias = list[tuple[str, Attrs]]
Item: TypeAlias = hdl.Param | hdl.Port

_RE_WIDTH = re.compile(r"\[([^\:]+)\s*\:\s*([^\]+])\](.*)")
_RE_MINUS1 = re.compile(r"(.+?)(-\s*1)")
DIRMAP = {"input": u.IN, "output": u.OUT, "inout": u.INOUT}


def import_params_ports(
    mod: u.BaseMod,
    filelistname: str = "hdl",
    filepath: Path | None = None,
    paramattrs: AttrsDict | AttrsList | None = None,
    constattrs: AttrsDict | AttrsList | None = None,
    portattrs: AttrsDict | AttrsList | None = None,
) -> None:
    """Import Parameter and Ports."""
    importer = SvImporter()
    if paramattrs:
        importer.add_paramattrs(paramattrs)
    if constattrs:
        importer.add_constattrs(constattrs)
    if portattrs:
        importer.add_portattrs(portattrs)
    importer(mod, filelistname=filelistname, filepath=filepath)


class SvImporter(u.Object):
    """Importer."""

    paramattrs: AttrsList = u.Field(default_factory=list)
    constattrs: AttrsList = u.Field(default_factory=list)
    portattrs: AttrsList = u.Field(default_factory=list)

    def add_paramattrs(self, paramattrs: AttrsDict | AttrsList) -> None:
        """Add Parameter Attributes."""
        if isinstance(paramattrs, dict):
            paramattrs = paramattrs.items()
        self.paramattrs.extend(paramattrs)

    def add_constattrs(self, constattrs: AttrsDict | AttrsList) -> None:
        """Add Constant Attributes."""
        if isinstance(constattrs, dict):
            constattrs = constattrs.items()
        self.constattrs.extend(constattrs)

    def add_portattrs(self, portattrs: AttrsDict | AttrsList) -> None:
        """Add Port Attributes."""
        if isinstance(portattrs, dict):
            portattrs = portattrs.items()
        self.portattrs.extend(portattrs)

    def add_name_paramattrs(self, name: str, attrs: Attrs) -> None:
        """Add Parameter Attributes For `name`."""
        self.paramattrs.append((name, attrs))

    def add_name_constattrs(self, name: str, attrs: Attrs) -> None:
        """Add Constant Attributes For `name`."""
        self.constattrs.append((name, attrs))

    def add_name_portattrs(self, name: str, attrs: Attrs) -> None:
        """Add Port Attributes For `name`."""
        self.portattrs.append((name, attrs))

    def __call__(
        self,
        mod: u.BaseMod,
        filelistname: str = "hdl",
        filepath: Path | None = None,
        no_params: bool = False,
        no_consts: bool = False,
        no_ports: bool = False,
    ) -> None:
        """
        Import Parameter, Constants and Ports.

        Args:
            mod: Module which will receive parameters, constant and ports.

        Keyword Args:
            filelistname: Name of filelist which will be looked up in `mod.filelists`.
            filepath: Explicit File Path.
            no_params: Skip Import of Parameter
            no_consts: Skip Import of Constants
            no_ports: Skip Import of Ports
        """
        filepath = filepath or self._find_filepath(mod, filelistname)
        file = hdl.parse_file(filepath)
        for module in file.modules:
            if module.name == mod.modname:
                if not no_params:
                    self._import_params(mod, self.paramattrs, module.params, mod.add_param)
                if not no_consts:
                    self._import_params(mod, self.constattrs, module.localparams, mod.add_const)
                if not no_ports:
                    self._import_ports(mod, module.ports)
                break
        else:
            raise ValueError(f"{filepath} does not contain module {mod.modname}")

    def _import_params(self, mod: u.BaseMod, paramattrs: AttrsList, params: tuple[hdl.Param, ...], add_func) -> None:
        paramdict = self._by_name(mod, params)
        while paramdict:
            param = paramdict.get(next(iter(paramdict.keys())))  # first element
            # struct?
            type_, name, attrs = self._find_type(mod, paramattrs, param.name, paramdict)
            if type_ is None:
                # no struct - scalar type
                attrs = self._find_attrs(paramattrs, param.name)
                type_ = self._get_param_type(mod, param)
            # create
            if param.ifdefs:
                attrs.setdefault("ifdefs", param.ifdefs)
            add_func(type_, name, **attrs)

    def _get_param_type(self, mod: u.BaseMod, param: hdl.Param) -> u.BaseType:
        type_ = self._get_type(mod, param)
        if param.default:
            parsed_default = SvImporter._parse(mod, param.default)
            if type_:
                try:
                    type_ = type_.new(default=parsed_default)
                except TypeError:
                    pass
            elif isinstance(parsed_default, u.Expr):
                type_ = parsed_default.type_
            else:
                type_ = self._get_param_defaulttype(default=parsed_default)
        elif not type_:
            type_ = self._get_param_defaulttype()
        return type_

    def _get_param_defaulttype(self, **kwargs) -> u.BaseType:
        return u.IntegerType(**kwargs)

    def _import_ports(self, mod: u.BaseMod, ports: tuple[hdl.Port, ...]) -> None:
        portdict = self._by_name(mod, ports)
        while portdict:
            port = portdict.get(next(iter(portdict.keys())))  # first element
            # struct?
            direction = DIRMAP[port.direction]
            type_, name, attrs = self._find_type(mod, self.portattrs, port.name, portdict, direction=direction)
            if type_ is None:
                # no struct - scalar type
                attrs = self._find_attrs(self.portattrs, port.name)
                type_ = self._get_type(mod, port) or self._get_port_defaulttype()
            # create
            if port.ifdefs:
                attrs.setdefault("ifdefs", port.ifdefs)
            mod.add_port(type_, name, direction=direction, **attrs)

    def _get_port_defaulttype(self) -> u.BaseType:
        return u.BitType()

    @staticmethod
    def _by_name(mod: u.BaseMod, items: tuple[Item, ...]) -> dict[str, Item]:
        itemdict = {}
        for item in items:
            ifdefs = u.resolve_ifdefs(mod.defines, item.ifdefs)
            if ifdefs is None:
                # disabled by ifdef
                continue
            added = itemdict.setdefault(item.name, item)
            if added is not item:
                raise ValueError(
                    f"{item.name!r} is duplicate due to ifdefs. "
                    f"Please set defines on {mod!r} for either {added.ifdefs} or {item.ifdefs}"
                )
        return itemdict

    @staticmethod
    def _find_filepath(mod: u.BaseMod, filelistname: str) -> Path:
        modfilelist = u.resolve_modfilelist(mod, filelistname, replace_envvars=True)
        if not modfilelist:
            raise ValueError(f"No filelist {filelistname!r} found.")

        try:
            return modfilelist.filepaths[0]
        except IndexError:
            raise ValueError(f"Filelist {filelistname!r} has empty 'filepaths'.") from None

    @staticmethod
    def _find_attrs(attrslist: AttrsList, name: str) -> Attrs:
        for pattern, attrs in attrslist:
            if pattern == name or match(name, pattern):
                if attrs.get("type_") is not None:
                    # handled by _find_type
                    continue
                return dict(attrs)  # ensure attrslist is not damaged, as keys/values might get manipulated
        return {}

    def _find_type(  # noqa: C901, PLR0912
        self,
        mod: u.BaseMod,
        attrslist: AttrsList,
        name: str,
        itemdict: dict[str, Item],
        direction: u.Direction | None = None,
    ) -> tuple[u.BaseType, str, Attrs] | None:
        matches: list[
            tuple[
                int,  # number of matches
                u.BaseType,  # type_
                str,  # name
                tuple[str, ...],  # obsolete names - strips
                Attrs,  # attributes
            ]
        ] = []
        for pattern, attrs in attrslist:
            if pattern == name or match(name, pattern):
                type_ = attrs.get("type_")
                if not type_:
                    # handled by _find_attrs
                    continue

                if isinstance(type_, u.BaseStructType):
                    # create ident with base-type and check that any member matches
                    if direction is None:
                        # just one flavor
                        idents = (u.Param(type_, "n"),)
                    else:
                        # with/without suffix
                        idents = (
                            u.Port(type_, "n_i", direction=u.IN),
                            u.Port(type_, "n_o", direction=u.OUT),
                            u.Port(type_, "n", direction=u.IN),
                            u.Port(type_, "n", direction=u.OUT),
                            u.Port(type_, "n", direction=u.INOUT),
                            u.Port(type_, "n_io", direction=u.INOUT),
                        )
                    for ident in idents:
                        # try to find ident where any subident.name matches `name`
                        submap = {sub.name.removeprefix("n"): sub for sub in ident.iter(filter_=_svfilter)}
                        for ending, subident in submap.items():
                            if name.endswith(ending) and subident.direction == direction:
                                # identifier found - create identifier with proper base name
                                ident = ident.new(name=f"{name.removesuffix(ending)}{ident.suffix}")
                                break
                        else:
                            # not matching
                            continue
                        # ensure all struct members have their friend
                        subs = tuple(ident.iter(filter_=_svfilter))
                        if not all(sub.name in itemdict for sub in subs):
                            continue
                        if isinstance(type_, u.DynamicStructType):
                            type_ = type_.new()
                            for item in itemdict.values():
                                if not item.name.startswith(ident.basename):
                                    continue
                                if any(sub.name == item.name for sub in subs):
                                    continue
                                subname = item.name.removeprefix(f"{ident.basename}_")
                                direction = getattr(item, "direction", None)
                                if direction is not None:
                                    subdirection = DIRMAP[direction] * ident.direction
                                else:
                                    subdirection = u.IN
                                subname = subname.removesuffix(subdirection.suffix)
                                type_.add(subname, self._get_type(mod, item), orientation=u.FWD * subdirection)
                            ident = ident.new(type_=type_)
                            subs = tuple(ident.iter(filter_=_svfilter))
                            print(subs)
                        # todo: check type
                        matches.append((len(subs), type_, ident.name, tuple(sub.name for sub in subs), attrs))
                        break
                else:
                    matches.append((1, type_, name, (name,), attrs))

        # sort identifier by number of subs
        matches = sorted(matches)

        # nothing found
        if not matches:
            itemdict.pop(name)
            return None, name, {}

        # use best match - highest number of covered subs
        _, type_, name, strips, attrs = matches[-1]
        # strip
        for strip in strips:
            itemdict.pop(strip)
        # strip type
        attrs = dict(attrs)
        attrs.pop("type_")
        return type_, name, attrs

    @staticmethod
    def _get_type(mod: u.BaseMod, item: Item) -> u.BaseMod | None:
        ptype = item.ptype
        dtype = getattr(item, "dtype", "").split(" ")
        dim = item.dim
        dim_unpacked = item.dim_unpacked

        type_ = None

        # Default Type
        if not ptype and not dim and not dim_unpacked:
            return type_

        if item.ptype == "integer":
            type_ = u.IntegerType()
        elif dim:
            width, left, right, sdir, dim = SvImporter._resolve_dim(mod, dim)
            # if sdir != u.DOWN:
            #     raise ValueError(f"{mod}: {dim} is not DOWNTO")
            if "signed" in dtype:
                type_ = u.SintType(width=width, right=right)
            else:
                type_ = u.UintType(width=width, right=right)
        else:
            type_ = u.BitType()

        while dim:
            width, left, right, sdir, dim = SvImporter._resolve_dim(mod, dim)
            type_ = u.ArrayType(type_, width, left=left, right=right, direction=sdir, packed=True)

        while dim_unpacked:
            width, left, right, sdir, dim_unpacked = SvImporter._resolve_dim(mod, dim_unpacked)
            type_ = u.ArrayType(type_, width, left=left, right=right, direction=sdir, packed=False)

        return type_

    @staticmethod
    def _resolve_dim(mod: u.BaseMod, dim: str) -> tuple[int | u.Expr, int | u.Expr, u.SliceDirection, str]:
        m = _RE_WIDTH.match(dim)
        if not m:
            raise ValueError(f"Unknown dimension {dim}")
        left, right, rem = m.groups()
        rexpr = SvImporter._parse(mod, right)
        lexpr = SvImporter._parse(mod, left)
        # determine width
        if lexpr >= rexpr:
            wexpr = SvImporter._plus1(mod, left, lexpr)
            if rexpr:
                wexpr -= rexpr
            sdir = u.DOWN
        else:
            wexpr = SvImporter._plus1(mod, right, rexpr)
            if lexpr:
                wexpr -= lexpr
            sdir = u.UP
        return wexpr, lexpr, rexpr, sdir, rem

    @staticmethod
    def _parse(mod: u.BaseMod, value: str) -> int | u.Expr:
        try:
            return int(value)
        except ValueError:
            return mod.parser(value)

    @staticmethod
    def _plus1(mod: u.BaseMod, value: str, expr: int | u.Expr) -> int | u.Expr:
        m = _RE_MINUS1.fullmatch(value)
        if m:
            return SvImporter._parse(mod, m.group(1))
        return expr + 1


def _svfilter(ident: u.Ident) -> bool:
    return not isinstance(ident.type_, u.BaseStructType)
