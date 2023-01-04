import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from subprocess import check_call
from tempfile import TemporaryDirectory
from typing import Union, Iterator


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


def check_shell(*args, **kwargs) -> None:
    """
    Wrapper around check_call, that enables shell and suppresses the return value.
    For easier use in doctests, where the return value adds unnecessary verbosity.
    """
    check_call(*args, shell=True, **kwargs)


def create_files(*filenames: Union[str, Path], cwd: Path = None):
    """
    Create empty files at the given names.
    If cwd is given, create them relative to that root.

        >>> tempdir = tempfile.TemporaryDirectory(prefix="create_files.")
        >>> create_files("readme.md", "src/main.c", "src/main.h", cwd=tempdir.name)
        >>> sorted(os.listdir(tempdir.name))
        ['readme.md', 'src']

        >>> sorted(os.listdir(tempdir.name + "/src"))
        ['main.c', 'main.h']
    """
    for filename in filenames:
        if cwd is not None:
            filename = Path(cwd) / filename
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        Path(filename).touch(exist_ok=True)


def make_temporary_directory(*args, **kwargs):
    """Wrapper around TemporaryDirectory, that keeps the directory
    alive until the end of execution and returns it as a Path object."""
    obj = TemporaryDirectory(*args, **kwargs)
    make_temporary_directory.items.add(obj)
    return Path(obj.name)


make_temporary_directory.items = set()
