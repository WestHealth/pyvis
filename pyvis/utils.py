# utility and helper functions for use in pyvis


def check_html(name):
    """
    Given a name of graph to save or write, check if it is of valid syntax

    :param: name: the name to check
    :type name: str
    """
    assert len(name.split(".")) >= 2, "invalid file type for %s" % name
    assert name.split(
        ".")[-1] == "html", "%s is not a valid html file" % name
