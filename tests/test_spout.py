#!/usr/bin/env python

"""Tests of spout managers."""

import tempfile

import pytest
import python_pachyderm
import tarfile
from os.path import join


def test_spout_manager():
    with tempfile.TemporaryDirectory(suffix="pachyderm") as d:
        manager = python_pachyderm.SpoutManager(pfs_directory=d, marker_filename="marker")

        with manager.commit() as commit:
            commit.put_file_from_bytes("foo1.txt", b"bar1")
            commit.put_marker_from_bytes(b"marker1")

        # Validate output
        with tarfile.open(join(d, "out"), "r|") as t:
            with t.extractfile("foo1.txt") as x:
                assert x.read() == b"bar1"
        with manager.marker() as m:
            assert m.read() == b"marker1"

        with manager.commit() as commit:
            commit.put_file_from_bytes("foo2.txt", b"bar2")
            commit.put_marker_from_bytes(b"marker2")

        # Validate output
        with tarfile.open(join(d, "out"), "r|") as t:
            with t.extractfile("foo2.txt") as x:
                assert x.read() == b"bar2"
        with manager.marker() as m:
            assert m.read() == b"marker2"

def test_spout_manager_nested_commits():
    with tempfile.TemporaryDirectory(suffix="pachyderm") as d:
        manager = python_pachyderm.SpoutManager(pfs_directory=d, marker_filename="marker")

        with manager.commit() as commit:
            commit.put_file_from_bytes("foo1.txt", b"bar1")
            commit.put_marker_from_bytes(b"marker1")

            with pytest.raises(Exception):
                with manager.commit() as commit:
                    pass

def test_spout_manager_commit_state():
    with tempfile.TemporaryDirectory(suffix="pachyderm") as d:
        manager = python_pachyderm.SpoutManager(pfs_directory=d, marker_filename="marker")

        for _ in range(3):
             with manager.commit() as commit:
                 raise Exception()
            assert !manager._has_open_commit

        # Now try to use the spout manager normally & confirm it still works
        with manager.commit() as commit:
            commit.put_file_from_bytes("foo1.txt", b"bar1")
            commit.put_marker_from_bytes(b"marker1")

        # Validate output
        with tarfile.open(join(d, "out"), "r|") as t:
            with t.extractfile("foo2.txt") as x:
                assert x.read() == b"bar2"
        with manager.marker() as m:
            assert m.read() == b"marker2"

