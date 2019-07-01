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

    @patch('canary.open', mock_open())
    def test_setconfig(self):
        patch('__main__.open', mock_open())
        curr_config = {"channels": []}
        canary.setconfig(curr_config)

    @patch('canary.open', mock_open(read_data = "{\"channels\": [\"DDD\"]}"))
    def test_getconfig(self):
        curr_config = {"channels": ["Nope"]}
        curr_config = canary.getconfig(curr_config)
        print(curr_config["channels"])
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
