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
"""IF-DEF Stress."""

import ucdp as u
from fileliststandard import HdlFileList


class IoType(u.AStructType):
    """IO."""

    title: str = "UART"
    comment: str = "RX/TX"

    def _build(self) -> None:
        self._add("rx", u.BitType(), u.BWD, ifdefs="X")
        self._add("tx", u.BitType(), u.FWD, ifdefs=("X", "Y"))


class IfdefMod(u.AMod):
    """IFDEF Stress Module."""

    filelists: u.ClassVar[u.ModFileLists] = (HdlFileList(gen="full"),)

    def _build(self) -> None:
        self.add_port(u.UintType(8), "a_i")
        self.add_port(u.UintType(8), "b_i", ifdefs=("A",))
        self.add_port(u.UintType(8), "j_i")

        sub0 = Sub0Mod(self, "u_sub0")
        sub0.con("a_i", "a_i")
        sub0.con("b_i", "b_i")
        Sub1Mod(self, "u_sub1")
        Sub2Mod(self, "u_sub2")
        Sub3Mod(self, "u_sub3")


class Sub0Mod(u.AMod):
    """Sub."""

    filelists: u.ClassVar[u.ModFileLists] = (HdlFileList(gen="full"),)

    def _build(self):
        self.add_port(u.UintType(8), "a_i")
        self.add_port(u.UintType(8), "b_i", ifdefs=("A",))
        self.add_port(u.UintType(8), "c_i", ifdefs=("B",))
        self.add_port(u.UintType(8), "d_i", ifdefs=("!B",))
        self.add_port(u.UintType(8), "e_i", ifdefs=("C",))
        self.add_port(u.UintType(8), "f_i", ifdefs=("C", "D"))
        self.add_port(u.UintType(8), "g_i", ifdefs=("D",))
        self.add_port(u.UintType(8), "h_i", ifdefs=("D", "E"))
        self.add_port(u.UintType(8), "i_i", ifdefs=("D"))
        self.add_port(u.UintType(8), "j_i")


class Sub1Mod(u.AMod):
    """Sub."""

    filelists: u.ClassVar[u.ModFileLists] = (HdlFileList(gen="full"),)

    def _build(self):
        self.add_port(u.UintType(8), "k_i", ifdefs=("B",))
        self.add_port(u.UintType(8), "l_i", ifdefs=("D", "E"))
        self.add_port(u.UintType(8), "m_i", ifdefs="E")


class Sub2Mod(u.AMod):
    """Sub."""

    filelists: u.ClassVar[u.ModFileLists] = (HdlFileList(gen="full"),)

    def _build(self):
        self.add_port(u.UintType(8), "q_i")
        self.add_port(IoType(), "r_i", ifdefs=("B",))
        self.add_port(u.UintType(8), "s_i", ifdefs=("D", "E"))
        self.add_port(u.UintType(8), "t_i")


class Sub3Mod(u.AMod):
    """Sub."""

    filelists: u.ClassVar[u.ModFileLists] = (HdlFileList(gen="full"),)

    def _build(self):
        mywidth = u.Define("_MYWIDTH", value=4)
        mydefault = u.Define("_MYDEFAULT", value=2)
        self.add_port(u.UintType(mywidth, default=mydefault), "q_i")
        self.add_port(u.UintType(8), "t_i")
