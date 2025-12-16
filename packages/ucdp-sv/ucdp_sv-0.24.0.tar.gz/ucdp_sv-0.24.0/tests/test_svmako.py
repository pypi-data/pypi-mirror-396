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
"""Test sv.mako."""

import os
from shutil import copytree
from unittest import mock

import ucdp as u
from test2ref import assert_refdata


def test_top(example, tmp_path):
    """Top Module."""
    copytree(example / "src", tmp_path, dirs_exist_ok=True)
    top = u.load("top.top")
    with mock.patch.dict(os.environ, {"PRJ": str(tmp_path)}):
        u.generate(top.mod, "hdl")

    assert_refdata(test_top, tmp_path)


def test_top_create(example, tmp_path):
    """Top Module."""
    copytree(example / "src", tmp_path, dirs_exist_ok=True)
    top = u.load("top.top")
    with mock.patch.dict(os.environ, {"PRJ": str(tmp_path)}):
        u.generate(top.mod, "hdl", create=True)

    assert_refdata(test_top_create, tmp_path)


def test_mux(example, tmp_path):
    """Top Module."""
    copytree(example / "src", tmp_path, dirs_exist_ok=True)
    top = u.load("top.mux")
    with mock.patch.dict(os.environ, {"PRJ": str(tmp_path)}):
        u.generate(top.mod, "hdl")

    assert_refdata(test_mux, tmp_path)


def test_ifdef(example, tmp_path):
    """Ifdef Module."""
    top = u.load("top.ifdef")
    with mock.patch.dict(os.environ, {"PRJ": str(tmp_path)}):
        u.generate(top.mod, "hdl")

    assert_refdata(test_ifdef, tmp_path)
