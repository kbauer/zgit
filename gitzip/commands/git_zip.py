import logging
from argparse import ArgumentParser, RawTextHelpFormatter
from inspect import cleandoc
from os import listdir
from pathlib import Path
from subprocess import check_call

from gitzip.lib.gitutil import git_get_gitzip_file, git_get_root_directory
from gitzip.lib.testutil import check_shell, create_files, make_temporary_directory


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

        >>> repo_path = make_temporary_directory(prefix="do_pack.")
        >>> create_files("src/main.c", "src/main.h", cwd=repo_path)
        >>> check_shell('git init && git add . && git commit -m "initial commit"', cwd=repo_path)

    Normally such git repositories are somewhat large.

        >>> assert len(list(repo_path.glob("**/*"))) > 20

    After packing, only a single file is left:

        >>> check_shell("git zip pack", cwd=repo_path)
        >>> listdir(repo_path/".git")
        ["gitzip.zip"]
    """
    gitzip_file: Path = git_get_gitzip_file()
    git_root: Path = git_get_root_directory()

    if gitzip_file.exists():
        logging.error("Already exists: %s", gitzip_file)
        exit(1)

    check_call(
        ["zip", "-rm0", str(gitzip_file.relative_to(git_root)),
         "--", *listdir(git_root)],
        cwd=git_root)


if __name__ == "__main__":
    main()
