import unittest
from unittest.mock import MagicMock,patch,mock_open
import sumosv
import canary


class Slack_Client:
    def api_call(self):
        pass
    def rtm_connect(self):
        pass

class Queue:
    def enqueue(self):
        pass


slack_client = patch("__main__.Slack_Client")
q = patch("__main__.Queue")

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
    
    #Test basic alert functionality; all this test cares about is whether it runs.
    def test_sumo(self):
        client = sumosv.app.test_client()
        user="ABSOLUTEBARGAIN99"
        with sumosv.app.app_context():
            dummydata = {"Hotel": "Trivago"}
            q.enqueue = MagicMock()
            sumosv.q = q
            output = client.post("/alert",headers={"Authorization": "Basic {user}".format(user=user)},data = dummydata)
            assert(output)

    #Test alert functionality when credentials correct.
    def test_sumo_authsuccess(self):
        client = sumosv.app.test_client()
        sumosv.users={"test_user":sumosv.generate_password_hash("test_password")}
        test_b64="dGVzdF91c2VyOnRlc3RfcGFzc3dvcmQ=" #B64-encoded version of "test_user:test_password"
        with sumosv.app.app_context():
            dummydata = {"Hotel": "Trivago"}
            q.enqueue = MagicMock()
            sumosv.q = q
            dummyjson=canary.json.dumps(dummydata)
            dummyjsonasbytes=dummyjson.encode('utf-8')
            output = client.post("/alert",headers={"Authorization": "Basic {user}".format(user=test_b64), 'Content-Length': len(dummyjson), "Content-Type": "application/json; charset=utf-8"}, data = canary.json.dumps(dummydata))
            assert(output.status_code == 200)
    
    #Test alert functionality when credentials incorrect.
    def test_sumo_authfail(self):
        client = sumosv.app.test_client()
        user="ABSOLUTEBARGAIN99"
        with sumosv.app.app_context():
            dummydata = {"Hotel": "Trivago"}
            q.enqueue = MagicMock()
            sumosv.logging.info = MagicMock()
            sumosv.q = q
            output = client.post("/alert",headers={"Authorization": "Basic {user}".format(user=user)},data = dummydata)
            assert(output.status_code == 401)