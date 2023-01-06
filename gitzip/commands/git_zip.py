import logging
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


if __name__ == "__main__":
    main()
