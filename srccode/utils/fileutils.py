import os


def drop_extension(path: str) -> str:
    """


    >>> drop_extension('../data/example.bin')
    '../data/example'

    :param path:
    :return: filepath without extension
    """
    filename, _ = os.path.splitext(path)
    return filename


def get_extension(path: str) -> str:
    """

    >>> get_extension('../data/example.bin')
    '.bin'

    :param path:
    :return: extension of path
    """
    _, extension = os.path.splitext(path)
    return extension


def is_bin_file(path: str) -> bool:
    """ Return True if path end with .bin, false otherwise.

    >>> is_bin_file('../data/example.bin')
    True

    >>> is_bin_file('../data/example.csv')
    False

    :param path:
    :return:
    """
    return get_extension(path) == ".bin"


if __name__ == '__main__':
    # https://docs.python.org/3/library/doctest.html#module-doctest
    import doctest

    doctest.testmod()
