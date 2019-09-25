# this unittest import is needed
import unittest
import os

import sol
# indicate the visibility of your test 

# all test cases should be written in this class
class TestCases(unittest.TestCase):
    def test_user_submitted_file(self):
        assert [] == os.listdir()

    def test_user_submitted_file_two(self):
        assert sol.hi() != 5