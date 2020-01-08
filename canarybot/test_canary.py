import unittest
from unittest.mock import MagicMock,patch,mock_open
import canary

cfg_test = {
    "channels": [], 
    "deadline": 65, 
    "cmdlist_dir": { 
        "subscribe": "Add your account to the list for direct messaging.",
        "unsubscribe": "Remove your account from the direct messaging list."
    },
    "cmdlist_men": { 
        "list": "Add the current channel to the alert list.",
        "delist": "Remove the current channel from the alert list."
    }
}

class TestCanaryMethods(unittest.TestCase):
    
    def test_addchannel_success(self):
        canary.CONFIG_OPTIONS = cfg_test
        canary.slackcommon.setconfig = MagicMock()
        canary.logging.info = MagicMock()
        canary.addchannel("AAAAA")
        assert("AAAAA" in canary.CONFIG_OPTIONS["channels"])
        #Will fail test if channel not added.
    
    def test_addchannel_dupe(self):
        canary.CONFIG_OPTIONS = cfg_test
        canary.CONFIG_OPTIONS["channels"].append("AAAAA")
        canary.slackcommon.setconfig = MagicMock()
        canary.logging.info = MagicMock()
        canary.addchannel("AAAAA")
        assert(not canary.slackcommon.setconfig.called)
        #Will fail test if channel duplicated (setconfig always called after channel added)
    
    #Due to unittest having no undo method for MagicMock, rmchannel tests have been given an 'alphabetical advantage'.
    def test__rmchannel_success(self):
        canary.CONFIG_OPTIONS = cfg_test
        canary.CONFIG_OPTIONS["channels"].append("BBBBB")
        canary.slackcommon.setconfig = MagicMock()
        canary.logging.info = MagicMock()
        canary.rmchannel("BBBBB")
        assert("BBBBB" not in canary.CONFIG_OPTIONS["channels"])
        #Will fail test if channel not removed.
    
    def test__rmchannel_notlisted(self):
        canary.CONFIG_OPTIONS = cfg_test
        canary.slackcommon.setconfig = MagicMock()
        canary.logging.info = MagicMock()
        canary.rmchannel("BBBBB")
        assert(not canary.slackcommon.setconfig.called)
        #Will fail test if attempted to remove nonexistent channel.
    
    #Not adding test function for sendhelp(); it's just a 'middle man'.

    def test_dmhandler_subscribe(self):
        canary.CONFIG_OPTIONS = cfg_test
        canary.slackcommon.sendmsg = MagicMock()
        canary.addchannel = MagicMock()
        canary.dmhandler("CCCCC","subscribe")
        assert(canary.addchannel.called)
        #Will fail test if doesn't attempt to subscribe channel.
    
    def test_dmhandler_unsubscribe(self):
        canary.CONFIG_OPTIONS = cfg_test
        canary.slackcommon.sendmsg = MagicMock()
        canary.rmchannel = MagicMock()
        canary.dmhandler("CCCCC","unsubscribe")
        assert(canary.rmchannel.called)
        #Will fail test if doesn't attempt to unsubscribe channel.

    def test_dmhandler_help(self):
        canary.CONFIG_OPTIONS = cfg_test
        canary.slackcommon.sendmsg = MagicMock()
        canary.sendhelp = MagicMock()
        canary.dmhandler("CCCCC","help")
        assert(canary.sendhelp.called)
        #Will fail test if doesn't attempt to send help message.
    
    #Skipping dmhandler printstate test as it's a simple debug function not intended for 'serious' use.

    def test_dmhandler_none(self):
        canary.CONFIG_OPTIONS = cfg_test
        canary.slackcommon.sendmsg = MagicMock()
        canary.addchannel = MagicMock()
        canary.rmchannel = MagicMock()
        canary.sendhelp = MagicMock()
        canary.dmhandler("CCCCC","greetings")
        assert(not canary.addchannel.called)
        assert(not canary.rmchannel.called)
        assert(not canary.sendhelp.called)

    def test_mentionhandler_list(self):
        canary.CONFIG_OPTIONS = cfg_test
        canary.slackcommon.sendmsg = MagicMock()
        canary.addchannel = MagicMock()
        canary.mentionhandler("DDDDD","list")
        assert(canary.addchannel.called)
        #Will fail test if doesn't attempt to subscribe channel.
    
    def test_mentionhandler_delist(self):
        canary.CONFIG_OPTIONS = cfg_test
        canary.slackcommon.sendmsg = MagicMock()
        canary.rmchannel = MagicMock()
        canary.mentionhandler("DDDDD","delist")
        assert(canary.addchannel.called)
        #Will fail test if doesn't attempt to unsubscribe channel.
    
    def test_mentionhandler_help(self):
        canary.CONFIG_OPTIONS = cfg_test
        canary.slackcommon.sendmsg = MagicMock()
        canary.sendhelp = MagicMock()
        canary.mentionhandler("DDDDD","help")
        assert(canary.sendhelp.called)
    
    def test_mentionhandler_none(self):
        canary.CONFIG_OPTIONS = cfg_test
        canary.slackcommon.sendmsg = MagicMock()
        canary.addchannel = MagicMock()
        canary.rmchannel = MagicMock()
        canary.sendhelp = MagicMock()
        canary.mentionhandler("DDDDD","greetings")
        assert(not canary.addchannel.called)
        assert(not canary.rmchannel.called)
        assert(not canary.sendhelp.called)

    def test_parse_incoming_direct(self):
        testevents = []
        testevent = {
            "type" : "message",
            "channel" : "DEEEE",
            "text" : "foo",
            "user" : "bar"
        }
        testevents.append(testevent)
        canary.logging.info = MagicMock()
        canary.dmhandler = MagicMock()
        canary.parse_incoming(testevents)
        assert(canary.dmhandler.called)
        #Will fail test if doesn't call dmhandler.
    
    def test_parse_incoming_mention(self):
        testevents = []
        testevent = {
            "type" : "message",
            "channel" : "EEEEE",
            "text" : "<@foo> test",
            "user" : "bar"
        }
        testevents.append(testevent)
        canary.canary_id = "foo"
        canary.logging.info = MagicMock()
        canary.mentionhandler = MagicMock()
        canary.parse_incoming(testevents)
        assert(canary.mentionhandler.called)
    
    def test_parse_incoming_none(self):
        testevents = []
        testevent = {
            "type" : "message",
            "channel" : "EEEEE",
            "text" : "test",
            "user" : "bar"
        }
        testevents.append(testevent)
        canary.canary_id = "foo"
        canary.logging.info = MagicMock()
        canary.mentionhandler = MagicMock()
        canary.dmhandler = MagicMock()
        canary.parse_incoming(testevents)
        assert(not canary.dmhandler.called)
        assert(not canary.mentionhandler.called)
    
    #Skipped get_id as it's just a call to a library function.