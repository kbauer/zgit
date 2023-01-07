# Zgit – single file git repositories

## 1. Motivation

When writing LaTeX documents, or when versioning small scripts,
I found it undesirable to have 40+ files just for the versioning.
Additionally, I was typically storing such files in Dropbox or similar
services, where repository corruption by synchronization issues could
accassionally become an issue – though Dropbox was generally very reliable
in that regard compared to other services, permission issues could sometimes
sabotage synchronization.

This package tries to solve this issue by packing *.git* repositories into a
single file and operating on that instead:

## 2. The commands

    zgit pack
        Convert an existing repository to single file format.

    zgit unpack
        Undo the pack command.

    zgit do [--] [GITCOMMAND...]
        Invoke the command GITCOMMAND... with $GIT_DIR pointing to
        a temporary directory containing the unpacked repository.

        If the command changes any files of the repository, the packed 
        version is updated accordingly.

## 3. Not ready for productive use

Currently, the package suffers from some issues:

1. `zgit do GITCOMMAND` suffers from poor performance. Caching of the
   unpacked repository would be desirable, but raises the complexity of the
   synchronization logic.
2. Tooling support is not ideal; Testing is needed to check which files must
   remain unpacked to avoid issues, e.g.
    - IDEs and other tools may use files like `COMMIT_EDITMSG`, or
      depend on the presence of not only the `.git` directory but also files
      within for detecting the root path of a project.
    - In the current form, git commands cannot be executed in parallel,
      which normally is possible. Personally, this comes up mostly with
      `git gui`.

Overall I recommend against using it for productive use at this point.
The issues also raise questions regarding whether I will actually go
forward with the project, as e.g. leaving files unpacked reduces the value
of the tool.


