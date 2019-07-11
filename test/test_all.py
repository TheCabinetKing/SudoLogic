import unittest

import sys
sys.path.append("..")

import test_sumo
from slackcommon import test_slackcommon
#New Canary tests not yet implemented.
##from canarybot import test_canary

from slackcommon import slackcommon as slackcommon_standin
test_slackcommon.slackcommon = slackcommon_standin

if(__name__ == "__main__"):
    totalsuite = unittest.TestSuite([test_sumo.suite(), test_slackcommon.suite()])
    runner=unittest.TextTestRunner()
    runner.run(totalsuite)