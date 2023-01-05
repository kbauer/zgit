import os
import subprocess
import tempfile
from contextlib import contextmanager
from os import mkdir, chdir
from pathlib import Path
from subprocess import check_call
from tempfile import TemporaryDirectory
from typing import Union, Iterator, Optional, Iterable


@contextmanager
def using_cwd(new_cwd: Union[Path, str]) -> Iterator[None]:
    """
    Context manager for switching working directory temporarily.

    >>> with tempfile.TemporaryDirectory() as tempdir:
    ...     original_cwd = Path.cwd()
    ...     with using_cwd(tempdir):
    ...         assert Path.cwd() == Path(tempdir)
    ...     assert Path.cwd() == original_cwd
    """
    old_cwd = Path.cwd()
    try:
        os.chdir(new_cwd)
        yield
    finally:
        os.chdir(old_cwd)


@contextmanager
def using_temp_cwd() -> Iterator[Path]:
    """
    Context manager that executes its body in a temporary directory.

    The context manager yields the temporary directory as Path object.

    >>> original_cwd = Path.cwd()
    >>> with using_temp_cwd() as tmpdir_path:
    ...     assert isinstance(tmpdir_path, Path)
    ...     assert Path.cwd() != original_cwd
    ...     assert tmpdir_path.exists()
    >>> assert not tmpdir_path.exists()
    """
    with TemporaryDirectory() as tmpdir:
        with using_cwd(tmpdir):
            yield Path(tmpdir)


def shell(*args, **kwargs) -> Optional[int]:
    """
    Wrapper around subprocess.call, that enables shell and suppresses the return value,
    unless it is non-zero.
    For easier use in doctests, where the return value adds unnecessary verbosity.
    """
    exit_code: int = subprocess.call(*args, shell=True, **kwargs)
    if exit_code == 0:
        return None
    else:
        return exit_code


def create_files(*filenames: str, cwd: Path = None):
    """
    Create empty files at the given names.
    If cwd is given, create them relative to that root.
    A path ending in / can be used to create an empty directory.

        >>> tempdir = tempfile.TemporaryDirectory(prefix="create_files.")
        >>> create_files("readme.md", "src/main.c", "src/main.h", "test/", cwd=tempdir.name)
        >>> ls(tempdir.name, recursive=True)
        readme.md
        src/main.c
        src/main.h
        test/
    """
    cwd: Path = (
        Path.cwd() if cwd is None else
        Path(cwd))

    for filename in filenames:
        full_path = cwd / filename
        full_path.parent.mkdir(parents=True, exist_ok=True)
        if filename.endswith("/"):
            full_path.mkdir(exist_ok=True)
        else:
            full_path.touch(exist_ok=True)


def make_temporary_directory(*args, **kwargs) -> Path:
    """Wrapper around TemporaryDirectory, that keeps the directory
    alive until the end of execution and returns it as a Path object."""
    obj = TemporaryDirectory(*args, **kwargs)
    make_temporary_directory.items.add(obj)
    return Path(obj.name)


make_temporary_directory.items = set()


def chdir2tmp(*args, **kwargs) -> None:
    """
    Create a temporary directory for the runtime of the program, and chdir to it.
    Parameters the same as C(tempfile.TemporaryDirectory).
    """
    tmpdir = make_temporary_directory(*args, **kwargs)
    os.chdir(tmpdir)


def ls(
        root: Optional[Union[str, Path]] = None,
        recursive: bool = False,
) -> None:
    """
    Print all the files in the directory for use in testing.

    Consider an example directory

        >>> chdir2tmp(prefix="dir_tree.")
        >>> create_files("a.txt", "test/", "src/b.txt", "src/c.txt")

    By default, the files in the current directory are printed,
    with subdirectories indicated by trailing /.

        >>> ls()
        a.txt
        src/
        test/

    With the 'recursive' option, the whole directory tree is printed.

        >>> ls(recursive=True)
        a.txt
        src/b.txt
        src/c.txt
        test/

    Paths are always printed relative to the root path

        >>> oldpwd = Path.cwd()
        >>> chdir("..")
        >>> ls(oldpwd)
        a.txt
        src/
        test/
    """
    root: Path = (
        Path.cwd() if root is None else
        Path(root))

    def print_recursively(path: Path):
        path_string: str = str(path.relative_to(root)).replace(os.sep, "/")
        if not path.is_dir():
            print(path_string)
        else:
            entries = sorted(path.glob("*"))
            if entries and recursive:
                for entry in entries:
                    print_recursively(entry)
            else:
                print(path_string + "/")

    for entry in root.glob("*"):
        print_recursively(entry)


def lstree(root: Optional[Union[str, Path]] = None):
    """
    Render the directory tree under root to stdout.

        >>> chdir2tmp()
        >>> create_files("main.c", "lib/string.c", "lib/string.h", "test/a.t", "test/b.t", "empty/")
        >>> lstree()
         |- empty/
         |- lib/
         |   |- string.c
         |   '- string.h
         |- main.c
         '- test/
             |- a.t
             '- b.t
    """
    root: Path = (
        Path.cwd() if root is None else
        Path(root))

    assert root.is_dir()

    def recur(directory: Path, prefix0: str = "", prefix1: str = ""):
        assert directory.is_dir()
        entries = sorted(directory.glob("*"))
        for idx, entry in enumerate(entries):
            is_last: bool = idx == len(entries) - 1
            if not entry.is_dir():
                if is_last:
                    print(prefix1 + " '- " + entry.name)
                else:
                    print(prefix1 + " |- " + entry.name)
            else:
                if is_last:
                    print(prefix1 + " '- " + entry.name + "/")
                    recur(entry, prefix0=prefix1 + " '- ", prefix1=prefix1 + "    ")
                else:
                    print(prefix1 + " |- " + entry.name + "/")
                    recur(entry, prefix0=prefix1 + " |- ", prefix1=prefix1 + " |  ")

    recur(root)
