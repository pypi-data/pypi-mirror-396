import os
import sys

from src.midir import (
    lsdir,
    midir,
    mipath,
    root_levels,
    root_suffix,
)

def make_lsdir_test_tree():
    os.system("mkdir level0")
    os.system("mkdir level0/level1a")
    os.system("mkdir level0/level1b")
    os.system("mkdir level0/level1c")
    os.system("touch level0/level1a/1.txt")
    os.system("touch level0/level1a/2.txt")
    os.system("touch level0/level1b/1.txt")

def clean_lsdir_test_tree():
    os.system("rm -r level0")


def goto_tests(func):
    def wrapper(*args, **kwargs):
        origin = os.getcwd()
        os.chdir(midir())
        out = func(*args, **kwargs)
        os.chdir(origin)
        return out
    return wrapper

@goto_tests
def make_lsdir_test_tree_wrapper(func):
    def wrapper(*args, **kwargs):
        make_lsdir_test_tree()
        out = func(*args, **kwargs)
        clean_lsdir_test_tree()
        return out
    return wrapper

def test_midir():
    #print(midir(__file__))
    assert midir().endswith("midir/tests")

def test_mipath():
    assert mipath().endswith("midir/tests/test_unit.py")

def test_root_levels():
    assert not [path for path in sys.path if path.endswith("/tests")]
    with_midir = [path for path in sys.path if path.endswith("/midir")]
    root_levels(levels=1)
    assert [path for path in sys.path if path.endswith("/tests")]
    root_levels(levels=2)
    assert with_midir == [path for path in sys.path if path.endswith("/midir")]

def test_root_suffix():
    assert '/Users/jordi' not in sys.path
    root_suffix("jordi")
    assert '/Users/jordi' in sys.path

def test_root_suffix_oserror():
    try:
        root_suffix("jona")
    except Exception:
        assert True

@goto_tests
@make_lsdir_test_tree_wrapper
def test_lsdir_files():
    assert lsdir("level0/level1a", return_full_path=False) == [
        "level0/level1a/1.txt",
        "level0/level1a/2.txt"

    ]
    assert lsdir("level0/level1a", folders=False, return_full_path=False) == [
        "level0/level1a/1.txt",
        "level0/level1a/2.txt"
    ]
    assert lsdir("level0/level1a", files=False, return_full_path=False) == []

@goto_tests
@make_lsdir_test_tree_wrapper
def test_lsdir_folders():
    assert lsdir("level0", files=False, return_full_path=False) == [
        "level0/level1a",
        "level0/level1b",
        "level0/level1c",

    ]
    assert lsdir("level0", folders=False, return_full_path=False) == []
    assert lsdir("level0", return_full_path=False) == [
        "level0/level1a",
        "level0/level1b",
        "level0/level1c",

    ]

@goto_tests
@make_lsdir_test_tree_wrapper
def test_lsdir_custom_filter():
    assert lsdir(
        "level0",
        files=False,
        folders=False,
        filter=lambda x: True if "1b" in x else False,
        return_full_path=False
    ) == ["level0/level1b"]
    _match = lsdir(
        "level0",
        files=False,
        folders=False,
        filter=lambda x: True if "1b" in x else False,
    ).pop()
    assert _match.endswith("level0/level1b")
    assert len(_match.replace("level0/level1b", "")) > 3



if __name__ == '__main__':
    test_midir()
    test_mipath()
    test_lsdir_files()
    test_lsdir_folders()
    test_lsdir_custom_filter()
    test_root_levels()
    test_root_suffix()
    test_root_suffix_oserror()