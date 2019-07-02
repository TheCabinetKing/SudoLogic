import unittest
from unittest.mock import MagicMock,patch,mock_open
import sumosv
import canary



class Slack_Client:
    def api_call():
        pass
    def rtm_connect():
        pass

class Queue:
    def enqueue():
        pass

class Request:
    def get_json():
        pass

slack_client = patch("__main__.Slack_Client")
q = patch("__main__.Queue")
request = patch("__main__.Request")

class TestCanaryMethods(unittest.TestCase):
    def test_alert_complete(self):
        data = {"AlertSource": "Intern Consulting", "AlertStatus": "Unimportant", "AlertThreshold": "Dehydration", "AlertID": "-000001"}
        slack_client.api_call = MagicMock(return_value = {"ok": True})
        canary.slack_client=slack_client
        canary.CONFIG_OPTIONS["channels"] = ["RXL931"]
        result = canary.alert(data)
        assert(result)
        #Will fail test if cannot parse data.

    def test_alert_incomplete(self):
        data = {"AlertStatus": "Unimportant", "AlertID": "-000001"}
        slack_client.api_call = MagicMock(return_value = {"ok": True})
        canary.slack_client=slack_client
        canary.CONFIG_OPTIONS["channels"] = ["RXL931"]
        result = canary.alert(data)
        assert(result)
        #Will fail test if cannot parse data.

    def test_alert_none(self):
        data = {}
        slack_client.api_call = MagicMock(return_value = {"ok": True})
        canary.slack_client=slack_client
        canary.CONFIG_OPTIONS["channels"] = ["RXL931"]
        result = canary.alert(data)
        assert(result)
        #Will fail test if cannot parse "data".

    def test_alert_api_down(self):
        data = {}
        slack_client.api_call = MagicMock(return_value = {"ok": False})
        canary.slack_client=slack_client
        canary.CONFIG_OPTIONS["channels"] = ["RXL931"]
        canary.CONFIG_OPTIONS["deadline"] = 2
        result = canary.alert(data)
        assert(result is False)
        #Will fail test if cannot detect API being down.

    @patch('canary.open', mock_open())
    def test_setconfig(self):
        patch('__main__.open', mock_open())
        curr_config = {"channels": []}
        canary.setconfig(curr_config)

    @patch('canary.open', mock_open(read_data = "{\"channels\": [\"DDD\"]}"))
    def test_getconfig(self):
        curr_config = {"channels": ["Nope"]}
        curr_config = canary.getconfig(curr_config)
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

class TestSumoMethods(unittest.TestCase):
    #As slackping is a set of function calls to canary, which has already been tested, its test has been omitted.
    #The alert function is similarly composed of function calls, making this test of dubious worth.
    def test_alert(self):
        with sumosv.app.app_context():
            dummydata = {"Hotel": "Trivago"}
            q.enqueue = MagicMock()
            request.get_json = MagicMock(return_value = dummydata)
            sumosv.q = q
            sumosv.request = request
            sumosv.jsonify = MagicMock(return_value = True)
            output = sumosv.getalert()
            assert(output)