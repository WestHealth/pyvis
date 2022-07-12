# utility and helper functions for use in pyvis
from html.parser import HTMLParser


def check_html(name):
    """
    Given a name of graph to save or write, check if it is of valid syntax

    :param: name: the name to check
    :type name: str
    """
    assert len(name.split(".")) >= 2, "invalid file type for %s" % name
    assert name.split(
        ".")[-1] == "html", "%s is not a valid html file" % name


class HREFParser(HTMLParser):

    count = 0
    count_changed = False

    """
    Given a string, check if it contains a valid href
    """
    def handle_starttag(self, tag, attributes):
        """
        Checks if the tags and attributes contain a valid href, returning True if one is detected, False otherwise
        """
        # Only parse tags where hrefs can appear
        if tag == "a":
            for name, value in attributes:
                if name == "href":
                    self.count += 1
                    self.count_changed = True

    def handle_endtag(self, tag: str):
        if tag == "a":
            self.count -= 1

    def is_valid(self) -> bool:
        return self.count == 0 and self.count_changed
