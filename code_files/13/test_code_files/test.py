# this unittest import is needed
import unittest
import sol

# all test cases should be written in this class
class TestCases(unittest.TestCase):
    @visible
    def test_user_submitted_file(self):
        assert sol.hi() == 5

    @not_visible
    def test_user_submitted_file_two(self):
        assert sol.hi() != 5