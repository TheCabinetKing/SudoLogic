import unittest

import sys
sys.path.append("..")

import test_sumo
from slackcommon import test_slackcommon
#New Canary tests not yet implemented.
##from canarybot import test_canary

if(__name__ == "__main__"):
    totalsuite = unittest.TestSuite([test_sumo.suite(), test_slackcommon.suite()])
    runner=unittest.TextTestRunner()
    runner.run(totalsuite)