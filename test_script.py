import unittest
from unittest.mock import MagicMock,patch,mock_open
import sumosv
import canary



class Slack_Client:
    def api_call():
        pass
    def rtm_connect():
        pass

slack_client = patch("__main__.Slack_Client")

class TestCanaryMethods(unittest.TestCase):
    def test_alert_complete(self):
        data = {"AlertSource": "Intern Consulting", "AlertStatus": "Unimportant", "AlertThreshold": "Dehydration", "AlertID": "-000001"}
        canary.alert(data)

    def test_alert_incomplete(self):
        data = {"AlertStatus": "Unimportant", "AlertID": "-000001"}
        canary.alert(data)

    def test_alert_none(self):
        data = {}
        canary.alert(data)

    @patch('__main__.open',mock_open())
    def test_setconfig(self):
        curr_config = {"channels": []}
        canary.setconfig(curr_config)

    @patch('__main__.open',mock_open(read_data="{\"channels\": [DDD]"))
    def test_getconfig(self):
        curr_config = {"channels": []}
        canary.getconfig(curr_config)
        assert(curr_config["channels"]==["DDD"])

    def test_handshake(self):
        slack_client.api_call=MagicMock(return_value = {"user_id": "yes"})
        slack_client.rtm_connect=MagicMock()
        canary.slack_client=slack_client
        canary.handshake()

    def test_handshake_fail(self):
        slack_client.api_call=MagicMock(return_value = {"error": "test_error_generic"})
        slack_client.rtm_connect=MagicMock()
        canary.slack_client=slack_client
        assert(canary.handshake() is False)
        return True

'''
#Failed and passed tests counters
testf=0
testp=0

if(test_alert_complete()):
    ++testp
else:
    ++testf
    print("FAILED: test_alert_complete")

if(test_alert_incomplete()):
    ++testp
else:
    ++testf
    print("FAILED: test_alert_incomplete")

if(test_alert_none()):
    ++testp
else:
    ++testf
    print("FAILED: test_alert_none")

if(test_getconfig()):
    ++testp
else:
    ++testf
    print("FAILED: test_getconfig")

if(test_handshake()):
    ++testp
else:
    ++testf
    print("FAILED: test_handshake")

if(test_handshake_fail()):
    ++testp
else:
    ++testf
    print("FAILED: test_handshake_fail")

if(test_setconfig()):
    ++testp
else:
    ++testf
    print("FAILED: test_setconfig")

print("\nSummary:\nPassed:\t{}\nFailed:\t{}".format(testp,testf))'''