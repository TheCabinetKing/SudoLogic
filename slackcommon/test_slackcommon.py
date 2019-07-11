import unittest
from unittest.mock import MagicMock,patch,mock_open
import slackcommon

class Slack_Client:
    def api_call(self):
        pass
    def rtm_connect(self):
        pass

slack_client = patch("__main__.Slack_Client")

class TestSlackCommonMethods(unittest.TestCase):
    def test_alert_complete(self):
        data = {"AlertSource": "Intern Consulting", "AlertStatus": "Unimportant", "AlertThreshold": "Dehydration", "AlertID": "-000001"}
        slack_client.api_call = MagicMock(return_value = {"ok": True})
        slackcommon.slack_client=slack_client
        slackcommon.CONFIG_OPTIONS["channels"] = ["RXL931"]
        result = slackcommon.alert(data)
        assert(result)
        #Will fail test if cannot parse data.

    def test_alert_incomplete(self):
        data = {"AlertStatus": "Unimportant", "AlertID": "-000001"}
        slack_client.api_call = MagicMock(return_value = {"ok": True})
        slackcommon.slack_client=slack_client
        slackcommon.CONFIG_OPTIONS["channels"] = ["RXL931"]
        result = slackcommon.alert(data)
        assert(result)
        #Will fail test if cannot parse data.

    def test_alert_none(self):
        data = {}
        slack_client.api_call = MagicMock(return_value = {"ok": True})
        slackcommon.slack_client=slack_client
        slackcommon.CONFIG_OPTIONS["channels"] = ["RXL931"]
        result = slackcommon.alert(data)
        assert(result)
        #Will fail test if cannot parse "data".

    def test_alert_api_down(self):
        data = {}
        slack_client.api_call = MagicMock(return_value = {"ok": False})
        slackcommon.slack_client=slack_client
        slackcommon.CONFIG_OPTIONS["channels"] = ["RXL931"]
        slackcommon.CONFIG_OPTIONS["deadline"] = 2
        result = slackcommon.alert(data)
        assert(result is False)
        #Will fail test if cannot detect API being down.

    @patch('slackcommon.open', mock_open())
    def test_setconfig(self):
        patch('__main__.open', mock_open())
        curr_config = {"channels": []}
        slackcommon.setconfig(curr_config)

    @patch('slackcommon.open', mock_open(read_data = "{\"channels\": [\"DDD\"]}"))
    def test_getconfig(self):
        curr_config = {"channels": ["Nope"]}
        curr_config = slackcommon.getconfig(curr_config)
        assert(curr_config["channels"]==["DDD"])

    def test_handshake(self):
        slack_client.api_call=MagicMock(return_value = {"user_id": "yes"})
        slack_client.rtm_connect=MagicMock()
        slackcommon.slack_client=slack_client
        slackcommon.handshake(slack_client)

    def test_handshake_fail(self):
        slack_client.api_call=MagicMock(return_value = {"error": "test_error_generic"})
        slack_client.rtm_connect=MagicMock()
        slackcommon.slack_client=slack_client
        assert(slackcommon.handshake(slack_client) is False)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSlackCommonMethods))
    return suite