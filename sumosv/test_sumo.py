import unittest
from unittest.mock import MagicMock,patch,mock_open
import sumosv
from slackcommon import slackcommon


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
            dummyjson=slackcommon.json.dumps(dummydata)
            dummyjsonasbytes=dummyjson.encode('utf-8')
            output = client.post("/alert",headers={"Authorization": "Basic {user}".format(user=test_b64), 'Content-Length': len(dummyjson), "Content-Type": "application/json; charset=utf-8"}, data = slackcommon.json.dumps(dummydata))
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

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSumoMethods))
    return suite