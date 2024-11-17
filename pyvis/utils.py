# utility and helper functions for use in pyvis


def check_html(filename: str):
    """
    Raise an AssertionError if the given filename does not end with '.html'

    :param: filename: the filename to check
    """
    assert filename.endswith('.html'), "filename %r must end with '.html'" % filename
