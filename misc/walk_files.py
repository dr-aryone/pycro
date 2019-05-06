#!/usr/bin/python3

def __walk_files(
        root,

        follow_symlinks = True,

        files = True,
        dirs = True,

        filter_function = lambda path: True,
        sort_func = sorted,
        ):

    walk_dirs = collections.deque([root])

    while walk_dirs:

        path = walk_dirs.popleft()

        for name in os.listdir(path):
            new_path = __joinpath(path, name)

            if __isdir(new_path):

                if dirs and filter_function(new_path):
                    yield new_path

                if __islink(new_path) and not follow_symlinks:
                    continue

                walk_dirs.append(new_path)

            elif __isfile(new_path):

                if files and filter_function(new_path):
                    yield new_path

            elif __exists(path):
                raise FileExistsError("{!r} exists, but it's not a "
                        "file or a directory.".format(new_path))

            else:
                raise FileNotFoundError(
                        "{!r} not exists, while exists in "
                        "os.listdir({!r})".format(name, path))

