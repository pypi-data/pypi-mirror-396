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
"""Example."""

import ucdp as u
from fileliststandard import HdlFileList
from glbl.bus import BusType
from glbl.clk_gate import ClkGateMod
from glbl.sync import SyncMod
from ucdp_glbl.stream import StreamType


class IoType(u.AStructType):
    """IO."""

    title: str = "UART"
    comment: str = "RX/TX"

    def _build(self) -> None:
        self._add("rx", u.BitType(), u.BWD, title="RX")
        self._add("tx", u.BitType(), u.FWD)


class SubMod(u.AMod):
    """Sub."""

    def _build(self):
        self.add_port(u.UintType(4), "in_i", title="title in_i", descr="descr in", comment="info about in")
        self.add_port(u.UintType(4), "open_i", title="title open_i", descr="descr open", comment="info about open")
        self.add_port(u.UintType(4), "open_o", title="title open_o", descr="descr open", comment="info about open")
        self.add_port(u.UintType(4), "note_i", title="title note_i", descr="descr note", comment="info about note")
        self.add_port(u.UintType(4), "note_o", title="title note_o", descr="descr note", comment="info about note")
        self.add_port(
            u.UintType(4), "default_i", title="title default_i", descr="descr default", comment="info about default"
        )
        self.add_port(
            u.UintType(4), "default_o", title="title default_o", descr="descr default", comment="info about default"
        )
        self.add_port(u.UintType(4), "unused_i")
        self.add_port(u.UintType(4), "unused_o")


class TopMod(u.AMod):
    """Top Module."""

    filelists: u.ClassVar[u.ModFileLists] = (HdlFileList(gen="full"),)

    def _build(self) -> None:  # noqa: PLR0915
        parser = self.parser

        param_p = self.add_param(u.IntegerType(default=10), "param_p")
        width_p = self.add_param(u.IntegerType(default=parser.log2(param_p + 1)), "width_p")
        default_p = self.add_param(u.UintType(param_p), "default_p")

        self.add_port(u.ClkRstAnType(), "main_i")
        self.add_port(IoType(), "intf_i", route="create(u_core/intf_i)", clkrel=u.ASYNC)
        self.add_port(BusType(), "bus_i", clkrel="main_clk_i")

        self.add_port(u.UintType(9), "brick_o", ifdefs="ASIC")

        self.add_port(u.UintType(param_p), "data_i")
        self.add_port(u.UintType(width_p), "cnt_o")
        self.add_port(StreamType(9), "key_i", clkrel="main_clk_i")
        self.add_port(u.UintType(4), "bidir_io")
        self.add_port(u.RailType(), "rail_i")
        self.add_port(u.RailType(), "rail_o")
        self.add_port(u.RailType(), "rail_io")

        self.add_port(u.UintType(9), "value_o", ifdefs="ASIC")

        self.add_const(u.UintType(param_p, default=default_p // 2), "const_c")

        self.add_signal(StreamType(9), "key_s")
        self.add_signal(u.UintType(4), "bidir_s")

        clkgate = ClkGateMod(self, "u_clk_gate")
        clkgate.con("clk_i", "main_clk_i")
        clkgate.con("clk_o", "create(clk_s)")

        core = TopCoreMod(self, "u_core", paramdict={"width_p": width_p, "param_p": param_p})
        param_p = core.add_param(u.IntegerType(default=10), "param_p")
        width_p = core.add_param(u.IntegerType(default=8), "width_p")
        core.add_param(u.SintType(8, default=-3), "other_p")

        core.add_port(u.ClkRstAnType(), "main_i")
        core.add_port(u.UintType(param_p), "p_i")
        core.add_port(u.UintType(param_p), "p_o")
        core.add_port(u.UintType(width_p, logic=False), "data_i")
        core.add_port(u.UintType(width_p), "data_o")
        core.add_port(u.UintType(9), "brick_o", ifdefs="ASIC")
        core.add_port(u.UintType(3), "some_i")
        core.add_port(u.UintType(2), "bits_i")

        core.add_port(StreamType(9), "key_i", clkrel="main_clk_i")
        core.con("key_i", "key_i")

        # open inputs/output
        core.add_port(u.RailType(), "open_rail_i")
        core.add_port(u.StringType(), "open_string_i")
        core.add_port(u.ArrayType(u.UintType(6), 4, direction=u.DOWN), "open_array_i")
        core.add_port(u.ArrayType(u.ArrayType(u.UintType(6), param_p), 2), "open_matrix_i")
        core.add_port(u.ArrayType(u.ArrayType(u.UintType(6), param_p, direction=u.DOWN), 2), "matrix_down_i")
        core.add_port(u.RailType(), "open_rail_o")
        core.add_port(u.StringType(), "open_string_o")
        core.add_port(u.ArrayType(u.UintType(6), 4), "open_array_o")
        core.add_port(u.ArrayType(u.ArrayType(u.UintType(6), 4, packed=True), 2), "open_matrix_o")

        core.add_port(u.UintType(7), "nosuffix0", direction=u.IN)
        core.add_port(u.UintType(7), "nosuffix1", direction=u.OUT)

        sync = SyncMod(self, "u_sync")
        sync.con("main_i", "main_i")

        SyncMod(self, "u_sync1", virtual=True)

        core.add_signal(u.UintType(width_p), "one_s")
        core.add_signal(u.UintType(width_p, logic=False), "two_s")
        core.add_signal(u.IntegerType(), "integer_s")
        core.add_signal(u.IntegerType(logic=False), "int_s")
        core.add_signal(u.FloatType(), "float_s")
        core.add_signal(u.DoubleType(), "double_s")

        core.add_port(u.ArrayType(u.UintType(8), param_p), "array_i")
        core.add_port(u.ArrayType(u.UintType(8), 8), "array_open_i")
        core.con("array_i", "create(array_s)")
        core.con("brick_o", "brick_o")

        core.con("main_clk_i", "clk_s")
        core.con("main_rst_an_i", "main_rst_an_i")

        core.con("some_i", "3h4")
        core.con("bits_i", "data_i[3:2]")

        self.route("key_s", "key_i")

        self.add_flipflop(u.UintType(9), "data_r", "main_clk_i", "main_rst_an_i", nxt="key_data_s")
        self.add_flipflop(u.UintType(param_p), "data2_r", "main_clk_i", "main_rst_an_i", nxt="data_i")

        self.assign("value_o", "key_data_s")
        # self.route("bidir_s", "bidir_io")

        sub = SubMod(self, "u_sub0")
        sub.con("in_i", "4'h4")
        sub.con("open_i", u.OPEN)
        sub.con("open_o", u.OPEN)
        sub.con("note_i", u.note("my note"))
        sub.con("note_o", u.note("other note"))
        sub.con("default_i", u.DEFAULT)
        sub.con("default_o", u.DEFAULT)
        sub.con("unused_i", u.UNUSED)
        sub.con("unused_o", u.UNUSED)


class TopCoreMod(u.ACoreMod):
    """Core Module."""

    filelists: u.ClassVar[u.ModFileLists] = (HdlFileList(gen="inplace"),)
