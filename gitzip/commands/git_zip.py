import logging
import os
from argparse import ArgumentParser, RawTextHelpFormatter
from glob import glob
from inspect import cleandoc
from os import listdir
from pathlib import Path
from pprint import pprint
from shutil import rmtree
from subprocess import check_call, DEVNULL

from gitzip.lib.gitutil import git_get_gitzip_file, git_get_root_directory
from gitzip.lib.testutil import shell, create_files, make_temporary_directory, chdir2tmp, ls


def main():
    parser = ArgumentParser(description=cleandoc("""
        Dispatches one of the following subcommands:
        
            git zip pack
                Convert git repository at hand to a git zip repository.
                
            git zip unpack
                Reverse the packing. Useful when intending to do operations,
                that are more easily performed on a regular zip repository.
                
            git zip SUBCOMMAND [ARGS...]
                Perform a git command on the zipped git directory.
                Internally, the repository is synchronized with a temporary
                unzipped location.
                
    """), formatter_class=RawTextHelpFormatter)
    parser.add_argument("subcommand", metavar="SUBCOMMAND")
    parser.add_argument("args", nargs="*", metavar="ARGS")
    options = parser.parse_args()

    if options.subcommand == "pack":
        if options.args:
            exit("Did not expect arguments, got: %r", options.args)
        do_pack()
        exit(0)

    elif options.subcommand == "unpack":
        if options.args:
            exit("Did not expect arguments, got: %r", options.args)
        do_unpack()
        exit(0)

    else:
        with using_temporary_git_directory():
            pass


def do_pack():
    """
    Command that performs the conversion of a git repository into a zipped
    git repository.

    Let us demonstrate with a dummy git repository:

        >>> chdir2tmp(prefix="do_pack.")
        >>> create_files("main.c", "lib/string.h", "lib/string.c")
        >>> shell('git init')
        >>> shell('git add .')
        >>> shell('git commit -m "initial commit"')

    Normally such git repositories are somewhat large.

        >>> assert len(list(Path.cwd().glob(".git/**/*"))) > 20

    After packing, only a single file is left,
    while the working set is left unchanged:

        >>> shell("git zip pack", stdout=DEVNULL)
        >>> ls(recursive=True)
        .git/gitzip.zip
        lib/string.c
        lib/string.h
        main.c
    """
    gitzip_file: Path = git_get_gitzip_file()
    git_root: Path = git_get_root_directory()
    git_dir: Path = git_root / ".git"

    if gitzip_file.exists():
        logging.error("Already exists: %s", gitzip_file)
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


def do_unpack():
    gitzip_file: Path = git_get_gitzip_file()
    git_root: Path = git_get_root_directory()


if __name__ == "__main__":
    main()
