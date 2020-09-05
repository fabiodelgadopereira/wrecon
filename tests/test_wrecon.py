import unittest
import sys
sys.path.append("..//wrecon//")
from wrecon import Tree
from wrecon import Wrecon

class Test(unittest.TestCase):

    def test_simple_tree(self):
        c= Tree("test")
        self.assertEqual(c.data, "test", "Most be test")

    def test_tree_with_nodes(self):
        a= Tree("test")
        b= Tree("node")
        a.children = b
        self.assertEqual(a.children.data, "node", "Most be node")
    
    def test_main_valid_max_urls(self):
        argv1 = ['-u', 'target', '-r', '1']
        parser = Wrecon.parse_args(argv1)
        self.assertEqual(parser.max_urls, 1)

    def test_main_valid_default_max_urls(self):
        argv1 = ['-u', 'target']
        parser = Wrecon.parse_args(argv1)
        self.assertEqual(parser.max_urls, 1),

    def test_main_valid_url(self):
        argv1 = ['--url target', '-r', '1']
        parser = Wrecon.parse_args(argv1)
        self.assertEqual(parser, 'target')

if __name__ == '__main__':
    unittest.main()