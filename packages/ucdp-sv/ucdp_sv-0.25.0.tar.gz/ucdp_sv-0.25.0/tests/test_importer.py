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
"""Test Importer."""

from pathlib import Path

import ucdp as u
from pytest import mark
from test2ref import assert_refdata

import ucdpsv as usv

from .conftest import TESTDATA


class TopMod(u.AMod):
    """Example Module."""

    filelists: u.ClassVar[u.ModFileLists] = (u.ModFileList(name="hdl", filepaths=("testdata/importer/top.sv",)),)

    def _build(self) -> None:
        usv.import_params_ports(self)


def test_verilog2ports():
    """Test verilog2ports."""
    top = TopMod()
    assert tuple(top.params) == (
        u.Param(u.IntegerType(default=10), "param_p"),
        u.Param(u.UintType(8, default=23), "generic_p"),
        u.Param(u.UintType(10, default=17), "generic2_p"),
        u.Param(u.IntegerType(default=1), "has_rx"),
        u.Param(u.IntegerType(default=1), "has_tx"),
    )
    assert tuple(repr(port) for port in top.ports) == (
        "Port(BitType(), 'main_clk_i', direction=IN)",
        "Port(BitType(), 'main_rst_an_i', direction=IN)",
        "Port(BitType(), 'intf_rx_o', direction=OUT)",
        "Port(BitType(), 'intf_tx_i', direction=IN)",
        "Port(UintType(2), 'bus_trans_i', direction=IN)",
        "Port(UintType(32), 'bus_addr_i', direction=IN)",
        "Port(BitType(), 'bus_write_i', direction=IN)",
        "Port(UintType(32), 'bus_wdata_i', direction=IN)",
        "Port(BitType(), 'bus_ready_o', direction=OUT)",
        "Port(BitType(), 'bus_resp_o', direction=OUT)",
        "Port(UintType(32), 'bus_rdata_o', direction=OUT)",
        "Port(BitType(), 'bus_other_i', direction=IN)",
        "Port(UintType(Param(IntegerType(default=10), 'param_p')), 'data_i', direction=IN)",
        "Port(UintType(Param(IntegerType(default=10), 'param_p')), 'cnt_o', direction=OUT)",
        "Port(UintType(9), 'brick_o', direction=OUT, ifdefs=('ASIC',))",
        "Port(BitType(), 'key_valid_i', direction=IN)",
        "Port(BitType(), 'key_accept', direction=OUT)",
        "Port(UintType(9), 'key_data', direction=IN)",
        "Port(UintType(4), 'bidir', direction=INOUT)",
        "Port(UintType(9), 'value_o', direction=OUT, ifdefs=('ASIC',))",
    )


class IoType(u.AStructType):
    """IO Type."""

    def _build(self) -> None:
        self._add("rx", u.BitType())
        self._add("tx", u.BitType(), orientation=u.BWD)


class BusType(u.AStructType):
    """Bus Type."""

    feature: bool = True
    hidden: bool = False

    def _build(self) -> None:
        self._add("trans", u.UintType(2))
        self._add("addr", u.UintType(32))
        self._add("write", u.BitType())
        self._add("wdata", u.UintType(32))
        if self.feature:
            self._add("ready", u.BitType(), orientation=u.BWD)
        self._add("resp", u.BitType(), orientation=u.BWD)
        self._add("rdata", u.UintType(32), orientation=u.BWD)
        if self.hidden:
            self._add("hidden", u.UintType(32), orientation=u.BWD)


class TopAttrsMod(u.AMod):
    """Example Module."""

    filelists: u.ClassVar[u.ModFileLists] = (u.ModFileList(name="hdl", filepaths=("testdata/importer/top.sv",)),)

    @property
    def modname(self) -> str:
        """Module Name."""
        return "top"

    def _build(self) -> None:
        usv.import_params_ports(
            self,
            portattrs=(
                ("main_clk_i", {"type_": u.ClkType()}),
                ("in*_tx_i", {"type_": u.BitType(default=1), "comment": "a comment"}),
                ("bus_*", {"type_": BusType(hidden=True)}),
                ("bus_*", {"type_": BusType(feature=False)}),
                ("bus_*", {"type_": BusType(feature=True)}),
            ),
        )


def test_verilog2ports_attrs():
    """Test verilog2ports."""
    top = TopAttrsMod()
    assert tuple(top.params) == (
        u.Param(u.IntegerType(default=10), "param_p"),
        u.Param(u.UintType(8, default=23), "generic_p"),
        u.Param(u.UintType(10, default=17), "generic2_p"),
        u.Param(u.IntegerType(default=1), "has_rx"),
        u.Param(u.IntegerType(default=1), "has_tx"),
    )
    assert tuple(repr(port) for port in top.ports) == (
        "Port(ClkType(), 'main_clk_i', direction=IN, doc=Doc(title='Clock'))",
        "Port(BitType(), 'main_rst_an_i', direction=IN)",
        "Port(BitType(), 'intf_rx_o', direction=OUT)",
        "Port(BitType(default=1), 'intf_tx_i', direction=IN, doc=Doc(comment='a comment'))",
        "Port(BusType(), 'bus_i', direction=IN)",
        "Port(BitType(), 'bus_other_i', direction=IN)",
        "Port(UintType(Param(IntegerType(default=10), 'param_p')), 'data_i', direction=IN)",
        "Port(UintType(Param(IntegerType(default=10), 'param_p')), 'cnt_o', direction=OUT)",
        "Port(UintType(9), 'brick_o', direction=OUT, ifdefs=('ASIC',))",
        "Port(BitType(), 'key_valid_i', direction=IN)",
        "Port(BitType(), 'key_accept', direction=OUT)",
        "Port(UintType(9), 'key_data', direction=IN)",
        "Port(UintType(4), 'bidir', direction=INOUT)",
        "Port(UintType(9), 'value_o', direction=OUT, ifdefs=('ASIC',))",
    )


class TopAttrs2Mod(u.AMod):
    """Example Module."""

    filelists: u.ClassVar[u.ModFileLists] = (u.ModFileList(name="hdl", filepaths=("testdata/importer/top.sv",)),)

    @property
    def modname(self) -> str:
        """Module Name."""
        return "top"

    def _build(self) -> None:
        usv.import_params_ports(
            self,
            paramattrs=(("has*", {"comment": "Hello is it me?"}),),
            portattrs=(
                ("main_clk_i", {"type_": u.ClkType()}),
                ("intf*", {"type_": IoType()}),
                ("bus_*", {"type_": BusType(feature=False)}),
            ),
        )


def test_verilog2ports_attrs2():
    """Test verilog2ports."""
    top = TopAttrs2Mod()
    assert tuple(top.params) == (
        u.Param(u.IntegerType(default=10), "param_p"),
        u.Param(u.UintType(8, default=23), "generic_p"),
        u.Param(u.UintType(10, default=17), "generic2_p"),
        u.Param(u.IntegerType(default=1), "has_rx"),
        u.Param(u.IntegerType(default=1), "has_tx"),
    )
    assert tuple(repr(port) for port in top.ports) == (
        "Port(ClkType(), 'main_clk_i', direction=IN, doc=Doc(title='Clock'))",
        "Port(BitType(), 'main_rst_an_i', direction=IN)",
        "Port(IoType(), 'intf_o', direction=OUT)",
        "Port(BusType(feature=False), 'bus_i', direction=IN)",
        "Port(BitType(), 'bus_ready_o', direction=OUT)",
        "Port(BitType(), 'bus_other_i', direction=IN)",
        "Port(UintType(Param(IntegerType(default=10), 'param_p')), 'data_i', direction=IN)",
        "Port(UintType(Param(IntegerType(default=10), 'param_p')), 'cnt_o', direction=OUT)",
        "Port(UintType(9), 'brick_o', direction=OUT, ifdefs=('ASIC',))",
        "Port(BitType(), 'key_valid_i', direction=IN)",
        "Port(BitType(), 'key_accept', direction=OUT)",
        "Port(UintType(9), 'key_data', direction=IN)",
        "Port(UintType(4), 'bidir', direction=INOUT)",
        "Port(UintType(9), 'value_o', direction=OUT, ifdefs=('ASIC',))",
    )


class DynBusType(u.DynamicStructType):
    """Dynamic Type Example."""

    def _build(self) -> None:
        self._add("addr", u.UintType(32))
        self._add("write", u.BitType())
        self._add("resp", u.BitType(), orientation=u.BWD)
        self._add("rdata", u.UintType(32), orientation=u.BWD)


class TopAttrsDynMod(u.AMod):
    """Example Module."""

    filelists: u.ClassVar[u.ModFileLists] = (u.ModFileList(name="hdl", filepaths=("testdata/importer/top.sv",)),)

    @property
    def modname(self) -> str:
        """Module Name."""
        return "top"

    def _build(self) -> None:
        usv.import_params_ports(
            self,
            portattrs=(
                ("main_clk_i", {"type_": u.ClkType()}),
                ("intf*", {"type_": IoType()}),
                ("key_*", {"type_": u.DynamicStructType()}),
                ("bus_*", {"type_": DynBusType()}),
            ),
        )


def test_verilog2ports_attrs_dyn():
    """Test verilog2ports."""
    top = TopAttrsDynMod()
    assert tuple(repr(port) for port in top.ports) == (
        "Port(ClkType(), 'main_clk_i', direction=IN, doc=Doc(title='Clock'))",
        "Port(BitType(), 'main_rst_an_i', direction=IN)",
        "Port(IoType(), 'intf_o', direction=OUT)",
        "Port(UintType(2), 'bus_trans_i', direction=IN)",
        "Port(DynBusType(), 'bus_i', direction=IN)",
        "Port(UintType(Param(IntegerType(default=10), 'param_p')), 'data_i', direction=IN)",
        "Port(UintType(Param(IntegerType(default=10), 'param_p')), 'cnt_o', direction=OUT)",
        "Port(UintType(9), 'brick_o', direction=OUT, ifdefs=('ASIC',))",
        "Port(BitType(), 'key_valid_i', direction=IN)",
        "Port(BitType(), 'key_accept', direction=OUT)",
        "Port(UintType(9), 'key_data', direction=IN)",
        "Port(UintType(4), 'bidir', direction=INOUT)",
        "Port(UintType(9), 'value_o', direction=OUT, ifdefs=('ASIC',))",
    )


class MatrixMod(u.AMod):
    """Matrix Module."""

    filelists: u.ClassVar[u.ModFileLists] = (u.ModFileList(name="hdl", filepaths=("testdata/importer/matrix.sv",)),)

    def _build(self) -> None:
        usv.import_params_ports(
            self,
            portattrs={
                "bus_*": {"type_": BusType()},
            },
        )


def test_verilog2ports_attrs_inout():
    """Test verilog2ports."""
    top = MatrixMod()
    assert tuple(top.params) == (
        u.Param(u.IntegerType(), "addrwidth"),
        u.Param(u.IntegerType(default=32), "datawidth_p"),
        u.Param(u.IntegerType(default=2), "tranwidth_p"),
    )
    assert tuple(repr(port) for port in top.ports) == (
        "Port(BitType(), 'main_clk_i', direction=IN)",
        "Port(BitType(), 'main_rst_an_i', direction=IN)",
        "Port(BitType(), 'intf_rx_o', direction=OUT, ifdefs=('TRAN',))",
        "Port(BitType(), 'intf_tx_i', direction=IN, ifdefs=('TRAN',))",
        "Port(BusType(), 'bus_a_i', direction=IN)",
        "Port(BusType(), 'bus_b_i', direction=IN)",
        "Port(BusType(), 'bus_c_o', direction=OUT)",
        "Port(BusType(), 'bus_m0', direction=IN)",
        "Port(BusType(), 'bus_s0', direction=OUT)",
    )


class ImportedMod(u.ATailoredMod):
    """Imported Module."""

    filepath: Path

    def _build(self) -> None:
        usv.import_params_ports(self, filepath=self.filepath)

    @property
    def modname(self):
        """Module Name."""
        return self.filepath.stem


DEFINES = {
    "ifdef_else": {"MOD_PARAM": 5},
    "ifdef_elif_95": {"VALUE": 5},
}


@mark.parametrize("filepath", TESTDATA.glob("sv/*"))
def test_sv(tmp_path: Path, filepath: Path):
    """SystemVerilog Examples."""
    defines = DEFINES.get(filepath.stem, None)
    mod = ImportedMod(filepath=filepath, defines=defines)
    info_path = tmp_path / f"{filepath.stem}.txt"
    with info_path.open("w") as file:
        for define in mod.defines or []:
            file.write(f"{define!r}\n")
        for param in mod.params:
            file.write(f"{param!r}\n")
        for port in mod.ports:
            file.write(f"{port!r}\n")
    assert_refdata(test_sv, tmp_path, flavor=filepath.stem)
