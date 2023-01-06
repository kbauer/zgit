import logging
import os
import shutil
import subprocess
import tempfile
from argparse import ArgumentParser, RawTextHelpFormatter
from inspect import cleandoc
from pathlib import Path
from shutil import rmtree
from subprocess import check_call, DEVNULL

from gitzip.lib.gitutil import git_get_gitzip_file, git_get_root_directory
from gitzip.lib.testutil import shell, create_files, chdir2tmp, lstree

logger = logging.getLogger("git-zip")


def main():
    parser = ArgumentParser(description=cleandoc("""
        Dispatches one of the following subcommands:
        
            git zip pack
                Convert git repository at hand to a git zip repository.
                
            git zip unpack
                Reverse the packing. Useful when intending to do operations,
                that are more easily performed on a regular zip repository.
                
            git zip do [--] SUBCOMMAND [ARGS...]
                Perform a git command on the zipped git directory.
                Internally, the repository is synchronized with a temporary
                unzipped location.
                
    """), formatter_class=RawTextHelpFormatter)
    parser.add_argument("subcommand", metavar="SUBCOMMAND")
    parser.add_argument("args", nargs="*", metavar="ARGS")
    options = parser.parse_args()

    if options.subcommand == "pack":
        if options.args:
            logger.error("Did not expect arguments, got: %r", options.args)
            exit(1)
        do_pack()

    elif options.subcommand == "unpack":
        if options.args:
            logger.error("Did not expect arguments, got: %r", options.args)
            exit(1)
        do_unpack()

    elif options.subcommand == "do":
        do_wrapped_subcommand(options.args)

    else:
        logger.error("Invalid subcommand: %s", options.subcommand)
        exit(1)


def do_pack():
    """
    Command that performs the conversion of a git repository into a zipped
    git repository.

    Let us demonstrate with a dummy git repository:

        >>> chdir2tmp()
        >>> create_files("main.c", "lib/string.h", "lib/string.c")
        >>> shell('git init')
        >>> shell('git add .')
        >>> shell('git commit -m "initial commit"')

    Normally such git repositories are somewhat large.

        >>> assert len(list(Path.cwd().glob(".git/**/*"))) > 20

    After packing, only a single file is left,
    while the working set is left unchanged:

        >>> shell("git zip pack", stdout=DEVNULL)
        >>> lstree()
         |- .git/
         |   '- gitzip.tgz
         |- lib/
         |   |- string.c
         |   '- string.h
         '- main.c
    """
    gitzip_file: Path = git_get_gitzip_file()
    git_root: Path = git_get_root_directory()
    git_dir: Path = git_root / ".git"

    if gitzip_file.exists():
        logger.error("Already exists: %s", gitzip_file)
        exit(1)

    # At least on windows, some files may be marked as read-only for some reason.
    for file_path in git_dir.glob("**/*"):
        file_path.chmod(0o777)

    entries_to_add = list(git_dir.glob("*"))
    check_call(
        ["tar", "czvf", str(gitzip_file.relative_to(git_dir)),
         "--", *(str(p.relative_to(git_dir)) for p in entries_to_add)],
        cwd=git_dir)
    for path in entries_to_add:
        if path.is_dir():
            rmtree(path)
        else:
            path.unlink()


def do_unpack() -> None:
    """
    Reverse peration of do_pack.

    Again, consider an example repository:

        >>> chdir2tmp()
        >>> create_files("main.c", "lib/string.h", "lib/string.c")
        >>> shell('git init', stdout=DEVNULL)
        >>> shell('git add .', stdout=DEVNULL)
        >>> shell('git commit -m "initial commit"', stdout=DEVNULL)

    Then the pack command reduces the number of files,

        >>> original_paths = set(Path.cwd().glob("**/*"))
        >>> shell("git zip pack", stdout=DEVNULL)
        >>> packed_paths = set(Path.cwd().glob("**/*"))
        >>> assert len(packed_paths) < len(original_paths)

    and the unpack command restores the original state.

        >>> shell("git zip unpack", stdout=DEVNULL)
        >>> unpacked_paths = set(Path.cwd().glob("**/*"))
        >>> assert original_paths == unpacked_paths

    """
    gitzip_file: Path = git_get_gitzip_file()
    git_root: Path = git_get_root_directory()
    git_dir: Path = git_root / ".git"

    if not gitzip_file.exists():
        logger.error("No such file: %s", gitzip_file)
        exit(1)

    check_call(
        ["tar", "xzvf", str(gitzip_file.relative_to(git_dir))],
        cwd=git_dir)

    gitzip_file.unlink()


def do_wrapped_subcommand(args: list[str]):
    """
    Execute git command on the unpacked git repository.

    If the git repository has changed after the command, update the
    single-file repository.

    Let us demonstrate with a dummy git repository:

        >>> chdir2tmp()
        >>> create_files("main.c", "lib/string.h", "lib/string.c")
        >>> shell('git init')
        >>> shell('git add .')
        >>> shell('git commit -m "initial commit"')
        >>> shell('git zip pack')

    A command that does not change the repository, will leave the repository file
    untouched.

        >>> stat_before = Path(".git/gitzip.tgz").stat()
        >>> shell("git zip do status", stdout=DEVNULL)
        >>> assert Path(".git/gitzip.tgz").stat() == stat_before
    """
    gitzip_file: Path = git_get_gitzip_file()
    if not gitzip_file.exists():
        logger.error("No such file: %s", gitzip_file)
        exit(1)

    gitzip_file_stat = gitzip_file.stat()

    with tempfile.TemporaryDirectory(prefix="gitzip.repository.") as temp_root:
        temp_root: Path = Path(temp_root)
        temp_repo: Path = temp_root / ".git"
        temp_repo.mkdir()
        temp_repo_file: Path = git_get_gitzip_file(relative_to=temp_root)
        shutil.copyfile(src=gitzip_file, dst=temp_repo_file)
        check_call(["git", "zip", "unpack"], stdout=DEVNULL, cwd=temp_root)
        state_before_command = {
            path: path.stat()
            for path in temp_repo.glob("**/*")
        }
        git_exit_code: int = subprocess.call(
            ["git", *args],
            env={**os.environ, "GIT_DIR": str(temp_repo.absolute())})
        state_after_command = {
            path: path.stat()
            for path in temp_repo.glob("**/*")
        }

        logger.info("Checking if repository has been changed by other command...")
        if not gitzip_file.exists():
            logger.error("File has been removed by some other command: %s", gitzip_file)
            exit(1)
        if not gitzip_file_stat.st_mtime == gitzip_file.stat().st_mtime:
            logger.error("File has been changed by some other command: %s", gitzip_file)
            exit(1)

        if state_before_command == state_after_command:
            logging.info("Repository did not change, no update needed.")
        else:
            logging.info("Repository changed, updating %s...", gitzip_file)
            check_call(["git", "zip", "pack"], stdout=DEVNULL, cwd=temp_root)
            temp_repo_file.replace(target=gitzip_file)

        if git_exit_code != 0:
            exit(git_exit_code)


if __name__ == "__main__":
    main()
