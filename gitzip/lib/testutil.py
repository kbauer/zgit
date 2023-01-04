import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
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
