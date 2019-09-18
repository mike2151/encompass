def visible(ob):
	return ob
def not_visible(ob):
	return ob
import sol
import unittest

class TestCases(unittest.TestCase):
    @visible
    def test_file(self):
        assert sol.hi() == 5

    @not_visible
    def test_file_two(self):
        assert sol.hi() == 4

