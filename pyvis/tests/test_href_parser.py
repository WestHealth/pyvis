import unittest
from pyvis.utils import HREFParser


class HreParserTestCase(unittest.TestCase):

    def test_valid_href(self):
        parser = HREFParser()
        test_text = '<a href="www.google.com"> Google </a>'
        parser.feed(test_text)
        self.assertTrue(parser.is_valid())

    def test_invalid_href(self):
        parser = HREFParser()
        test_text = '<a href="www.google.com"> Google </'
        parser.feed(test_text)
        self.assertFalse(parser.is_valid())

        parser = HREFParser()
        test_text = '< href="www.google.com"> Google </a>'
        parser.feed(test_text)
        self.assertFalse(parser.is_valid())

        parser = HREFParser()
        test_text = '<a class="www.google.com"> Google </a>'
        parser.feed(test_text)
        self.assertFalse(parser.is_valid())

    def test_empty_string(self):
        parser = HREFParser()
        test_text = ""
        parser.feed(test_text)
        self.assertFalse(parser.is_valid())

    def test_other_html_elements(self):
        parser = HREFParser()
        test_text = '<div href="www.google.com"> google </div>'
        parser.feed(test_text)
        self.assertFalse(parser.is_valid())
