import os #Used for token auth.
import time #Used for sleep to avoid network strain.
from slackclient import SlackClient
import json

token=os.environ.get('SLACK_BOT_TOKEN')
slack_client = None

canary_id = None

#Config options, as the name implies. Taken from config.ini, and used to communicate permitted channels etc. between instances.
CONFIG_OPTIONS = {
    "channels": [] #List of approved channels for posting.
}

#Returns Slack client instance. Used for more or less everything; this declaration is global in most applications.
def getclient(token):
    slack_client=SlackClient(token)
    return slack_client

#"Shorthand" for the API call needed to send a message to a channel.
def sendmsg(channel,tosend):
    slack_client.api_call("chat.postMessage",channel=channel,text=tosend)

#Takes a set of slack events and sorts through them for messages. This is the 'controller' for the chatbot side, and all new commands should be added here.
def parse_incoming(slack_events):
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            channel = event["channel"]
            msg = event["text"]
            msg = msg.strip(',.').lower()
            print(msg)
            #Subscription mechanics for direct messaging.
            if(channel.startswith('D')):
                #Subscription
                if(msg.startswith("subscribe")):
                    if channel not in CONFIG_OPTIONS["channels"]:
                        CONFIG_OPTIONS["channels"].append(channel)
                        setconfig(CONFIG_OPTIONS)
                    sendmsg(channel,"Subscription confirmed. If this is not in a private channel, please immediately deactivate me.")
                    return
                #Unsubscription
                if(msg.startswith("unsubscribe")):
                    if channel in CONFIG_OPTIONS["channels"]:
                        CONFIG_OPTIONS["channels"].remove(channel)
                        setconfig(CONFIG_OPTIONS)
                    sendmsg(channel,"Delisting successful.")
                    return
                #Remember to document all added commands in *both* help responsess!
                if(msg.startswith("help")):
                    sendmsg(channel,"All commands are directly messaged, or prefaced with a mention.")
                    sendmsg(channel,"Direct commands:\n\t*subscribe* - Add your account to the list for direct messaging.\n\t*unsubscribe* - Remove your account from the direct messaging list.\n")
                    sendmsg(channel,"Mention commands:\n\t*list* - Add the current channel to the alert list.\n\t*delist* - Remove the current channel from the alert list.")
            #Check for "@canarybot" etc.; direct mentions.
            if(msg.startswith("<@"+canary_id.lower()+">")):
                #Scrub mention so we can check the actual command.
                msg=msg.replace("<@"+canary_id.lower()+"> ",'')
                #Add current channel to alert list.
                if(msg.startswith("list")):
                    if channel not in CONFIG_OPTIONS["channels"]:
                        CONFIG_OPTIONS["channels"].append(channel)
                        setconfig(CONFIG_OPTIONS)
                        sendmsg(channel,"Confirmed; channel added to alert list.")
                    return
                #Remove current channel from alert list.
                if(msg.startswith("delist")):
                    if channel in CONFIG_OPTIONS["channels"]:
                        CONFIG_OPTIONS["channels"].remove(channel)
                        setconfig(CONFIG_OPTIONS)
                    sendmsg(channel,"Delisting successful.")
                    return
                #Remember to document all added commands in *both* help responsess!
                if(msg.startswith("help")):
                    sendmsg(channel,"All commands are directly messaged, or prefaced with a mention.")
                    sendmsg(channel,"Direct commands:\n\t*subscribe* - Add your account to the list for direct messaging.\n\t*unsubscribe* - Remove your account from the direct messaging list.\n")
                    sendmsg(channel,"Mention commands:\n\t*list* - Add the current channel to the alert list.\n\t*delist* - Remove the current channel from the alert list.")

#Sends alerts to Slack.
def alert(data):
    output = {"AlertSource": data.get("AlertSource","{Unknown Source}"), "AlertStatus": data.get("AlertStatus","{Unknown Status}"), "AlertThreshold": data.get("AlertThreshold","{Unknown Threshold}"), "AlertID": data.get("AlertID","{Unknown ID}")}
    for approved_channel in CONFIG_OPTIONS["channels"]:
        sendmsg(approved_channel,"Alert from {AlertSource} (status {AlertStatus}).\nReason: {AlertThreshold}\nID: {AlertID}".format(**output))
    #Empty dictionary in preparation for next in queue. Currently useless.
    data.clear()

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
def handshake():
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

#Used to assign canary_id.
def get_id():
    return slack_client.api_call("auth.test")["user_id"]

#Ensure only one message listener active.
if __name__ == "__main__":
    slack_client = getclient(token)
    CONFIG_OPTIONS = getconfig(CONFIG_OPTIONS)
    print("Config attained. Channel contents: ")
    for p in CONFIG_OPTIONS["channels"]: print(p)
    if handshake():
        canary_id = get_id()
        print("Connection established.")
        #Main loop; add all constant behaviour here, but be careful for slowdown.
        while True:
            parse_incoming(slack_client.rtm_read())
            time.sleep(0.5) #Avoid DOSing both sides by only checking once every 0.5 seconds.
    else:
        print("Connection failed; see traceback above for details.")