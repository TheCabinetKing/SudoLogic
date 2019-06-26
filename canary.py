import os #Used for token auth.
import time #used only for testing.
from slackclient import SlackClient
import json

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

canary_id = None

#Global constants.
PASSKEY = "217 Lambda" #Passkey to access testing. Used to avoid spam.
CONFIG_OPTIONS = { #Config options, as the name implies. Taken from config.ini, and used to communicate permitted channels etc. between instances.
    "channels": [] #List of approved channels for posting.
}



def parse_incoming(slack_events):
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            channel = event["channel"]
            msg = event["text"]
            msg.strip(',.').lower()
            #Subscription mechanics for direct messaging.
            if(channel.startswith('D')):
                #Subscription
                if(msg.startswith("subscribe")):
                    if channel not in CONFIG_OPTIONS["channels"]:
                        CONFIG_OPTIONS["channels"].append(channel)
                        setconfig(CONFIG_OPTIONS)
                    slack_client.api_call("chat.postMessage",channel=channel,text="Subscription confirmed. If this is not in a private channel, please immediately deactivate me.")
                    return
                #Unsubscription
                if(msg.startswith("unsubscribe")):
                    if channel in CONFIG_OPTIONS["channels"]:
                        CONFIG_OPTIONS["channels"].remove(channel)
                        setconfig(CONFIG_OPTIONS)
                    slack_client.api_call("chat.postMessage",channel=channel,text="Delisting successful.")
                    return
            else:
                print("Invalid channel detected. Response culled.")

def alert(data):
    #RQ uses this function to Do Stuff(tm). Placeholder data in the meantime.
    data = {"AlertThreshold": "Above 90 last 15 minutes", "AlertSource": "Intern Consulting, Co.", "AlertID": "164281", "AlertStatus": "Warning"}
    for approved_channel in CONFIG_OPTIONS["channels"]:
        slack_client.api_call("chat.postMessage",channel=approved_channel,text="Alert from {AlertSource} (status {AlertStatus}).\nReason: {AlertThreshold}\nID: {AlertID}".format(**data))
    #Empty dictionary in preparation for next in queue. Currently useless.
    data.clear()

#Overwrite config with current status.
def setconfig(config_tgt):
    config = open("config.ini",'w')
    json.dump(config_tgt,config)
    config.close()

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

def handshake():
    status = slack_client.rtm_connect(with_team_state=False)
    #Get bot ID from auth call. This will be useful for mention detection.
    canary_id = slack_client.api_call("auth.test")["user_id"]
    return status

#Ensure only one message listener active ('manual process').
if __name__ == "__main__":
    CONFIG_OPTIONS = getconfig(CONFIG_OPTIONS)
    print("Config attained. Channel contents: ")
    for p in CONFIG_OPTIONS["channels"]: print(p)
    if handshake():
        print("Connection established.")
        while True:
            parse_incoming(slack_client.rtm_read())
            time.sleep(0.5) #Avoid DOSing both sides by only checking once every 0.5 seconds.
    else:
        print("Connection failed; see traceback above for details.")