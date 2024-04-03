# utility and helper functions for use in pyvis
from os import PathLike
from pathlib import Path

def check_html(name: PathLike):
    """
    Given a name of graph to save or write, check if it is of valid syntax

    :param: name: the name to check
    :type name: PathLike
    """
    name = Path(name)
    if (name.suffix != ".html") or (name.suffixes[-1] != ".html"):
        raise ValueError(f"{name} is not a valid html file")
    if not name.parent.exists():
        # ensures that the parent folder exists and creates it if it doesn't exist
        name.parent.mkdir(parents=True, exist_ok=True)
