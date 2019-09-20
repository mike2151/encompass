from user_test import TestCases

import unittest
import sys
runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=2)
result = runner.run(unittest.makeSuite(TestCases))
