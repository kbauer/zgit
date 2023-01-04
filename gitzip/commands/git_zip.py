import logging
from argparse import ArgumentParser, RawTextHelpFormatter
from inspect import cleandoc
from subprocess import call


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
        exit(do_pack())

    elif options.subcommand == "unpack":
        if options.args:
            exit("Did not expect arguments, got: %r", options.args)
        exit(do_unpack())

    else:
        with using_temporary_git_directory():
            pass


def do_pack():
    """
    Command that performs the conversion of a git repository into a zipped
    git repository.

    >>> 

    :return:
    """





if __name__ == "__main__":
    main()