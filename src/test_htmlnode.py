import unittest
from htmlnode import HTMLNode 

class TestTextNode(unittest.TestCase):
    def test_props_eq(self):
        node = HTMLNode()
        self.assertEqual(node.props, None)
    
    def test_props_to_html_with_href(self):
        # Test with a link props
        node = HTMLNode("a", "Click me!", None, {"href": "https://boot.dev"})
        self.assertEqual(node.props_to_html(), ' href="https://boot.dev"')

    def test_value(self):
        node = HTMLNode("p", "hello world")
        self.assertEqual(node.value, "hello world")

if __name__ == "__main__":
    unittest.main()