import os #Used for token auth.
import time #Used for sleep to avoid network strain.
from slackclient import SlackClient
import json
import logging

token=os.environ.get('SLACK_BOT_TOKEN')
slack_client = None


canary_id = None

#Config options, as the name implies. Taken from config.ini, and used to communicate permitted channels etc. between instances.
CONFIG_OPTIONS = {
    "channels": [], #List of approved channels for posting.
    "deadline": 65, #Period the bot is willing to wait at once before giving up.  Used in alert().
    "cmdlist_dir": { #List of direct-message commands.
        "subscribe": "Add your account to the list for direct messaging.",
        "unsubscribe": "Remove your account from the direct messaging list."
    },
    "cmdlist_men": { #List of mention commands.
        "list": "Add the current channel to the alert list.",
        "delist": "Remove the current channel from the alert list."
    }
}

#Returns Slack client instance. Used for more or less everything; this declaration is global in most applications.
def getclient(token):
    slack_client=SlackClient(token)
    return slack_client

#"Shorthand" for the API call needed to send a message to a channel. Returns True if successful, False otherwise.
def sendmsg(channel,tosend):
    result = slack_client.api_call("chat.postMessage",channel=channel,text=tosend)
    return result["ok"]

#Sends alerts to Slack. Returns True if successful, False otherwise (timeout).
def alert(data):
    output = {
        "AlertSource": data.get("AlertSource","{Unknown Source}"),
        "AlertStatus": data.get("AlertStatus","{Unknown Status}"),
        "AlertThreshold": data.get("AlertThreshold","{Unknown Threshold}"),
        "AlertID": data.get("AlertID","{Unknown ID}")
    }
    logging.info("Propagating alert...")
    for approved_channel in CONFIG_OPTIONS["channels"]:
        result = sendmsg(approved_channel,"Alert from {AlertSource} (status {AlertStatus}).\nReason: {AlertThreshold}\nID: {AlertID}".format(**output))
        if(result is False):
            deadline = CONFIG_OPTIONS["deadline"]
            wait = 1
            while(result is False):
                time.sleep(wait)
                result = sendmsg(approved_channel,"Alert from {AlertSource} (status {AlertStatus}).\nReason: {AlertThreshold}\nID: {AlertID}".format(**output))
                wait *= 2
                if(wait>=deadline):
                    logging.error("Failed!")
                    return False
    logging.info("Done!")
    return True

#Overwrite config with current status.
def setconfig(config_tgt):
    config = open("config.ini",'w')
    json.dump(config_tgt,config)
    config.close()

#Config handler, called at the start of all canary instances, including alert propagators.
def getconfig(config_tgt):
    #Try to get current config
    try:
        config = open("config.ini",'r')
        config_tgt = json.load(config)
        config.close()
        return config_tgt
    #If config file not found, create one with default params.
    except FileNotFoundError:
        print("File not found. Setting new default...")
        setconfig(config_tgt)
        return config_tgt

#Establish connection and use auth.test to confirm server compliance.
def handshake(slack_client):
    status = slack_client.rtm_connect(with_team_state=False)
    #Get bot ID from auth call. This will be useful for mention detection.
    try:
        slack_client.api_call("auth.test")["user_id"]
    #Auth errors are usually issues involving tokens and env variables.
    except:
        print("Error authenticating:")
        print(slack_client.api_call("auth.test")["error"])
        return False
    return status