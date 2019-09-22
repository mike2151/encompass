def visible(ob):
	return ob
def not_visible(ob):
	return ob
import sol
import unittest

class TestCases(unittest.TestCase):
    def test_file(self):
        assert sol.hi() == 5

    def test_file_two(self):
        assert sol.hi() == 4

