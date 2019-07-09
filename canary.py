import os #Used for token auth.
import time #Used for sleep to avoid network strain.
from slackclient import SlackClient
import json
import logging

token=os.environ.get('SLACK_BOT_TOKEN')
slack_client = None
logging.basicConfig(filename="canary.log",filemode='a',format="%(asctime)s - %(name)s - %(levelname)s: %(message)s",datefmt="%y-%m-%d %H:%M:%S",level=logging.INFO)

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

#Add channel to authorised channel list.
def addchannel(channel):
    if channel not in CONFIG_OPTIONS["channels"]:
        CONFIG_OPTIONS["channels"].append(channel)
        logging.info("Added channel {0} to alert list".format(channel))
        setconfig(CONFIG_OPTIONS)

#Remove channel from authorised channel list.
def rmchannel(channel):
    if channel in CONFIG_OPTIONS["channels"]:
        CONFIG_OPTIONS["channels"].remove(channel)
        logging.info("Removed channel {0} from alert list".format(channel))
        setconfig(CONFIG_OPTIONS)

#Helper function for "help" command; commands can be added in the cmdlist variables. Remember that the existing config would override it!
def sendhelp(channel):
    sendmsg(channel,"All commands are directly messaged, or prefaced with a mention.")
    msgout = "Direct commands:\n"
    for command in CONFIG_OPTIONS["cmdlist_dir"]:
        msgout = msgout + ("\t*"+command+"*"+" - "+CONFIG_OPTIONS["cmdlist_dir"][command]+"\n")
    sendmsg(channel, msgout)
    msgout="Mention commands:\n"
    for command in CONFIG_OPTIONS["cmdlist_men"]:
        msgout = msgout + ("\t*"+command+"*"+" - "+CONFIG_OPTIONS["cmdlist_men"][command]+"\n")
    sendmsg(channel, msgout)
    logging.info("Help message sent to channel {0}".format(channel))

def dmhandler(channel,msg):
    #Subscription
    if(msg.startswith("subscribe")):
        addchannel(channel)
        sendmsg(channel,"Subscription confirmed.")
        return
    #Unsubscription
    if(msg.startswith("unsubscribe")):
        rmchannel(channel)
        sendmsg(channel,"Delisting successful.")
        return
    #Remember to document all added commands in *both* help responses!
    if(msg.startswith("help")):
        sendhelp(channel)

def mentionhandler(channel,msg):
    #Add current channel to alert list.
    if(msg.startswith("list")):
        addchannel(channel)
        sendmsg(channel,"Confirmed; channel added to alert list.")
        return
    #Remove current channel from alert list.
    if(msg.startswith("delist")):
        rmchannel(channel)
        sendmsg(channel,"Delisting successful.")
        return
    #Remember to document all added commands in *both* help responsess!
    if(msg.startswith("help")):
        sendhelp(channel)

#Takes a set of slack events and sorts through them for messages. This is the 'controller' for the chatbot side, and all new commands should be added here.
def parse_incoming(slack_events):
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            channel = event["channel"]
            msg = event["text"]
            logging.info("Message received from {0} in channel {1}, contents: {2}".format(event["user"],channel,msg))
            msg = msg.strip(',.').lower()
            #Command handling for direct messaging.
            if(channel.startswith('D')):
                dmhandler(channel,msg)
                return
            #Check for "@canarybot" etc.; direct mentions.
            if(msg.startswith("<@"+canary_id.lower()+">")):
                #Scrub mention so we can check the actual command.
                msg=msg.replace("<@"+canary_id.lower()+"> ",'')
                mentionhandler(channel,msg)
                return

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
    channel_ls="" #Log output variable, no use after for loop's log update.
    for p in CONFIG_OPTIONS["channels"]:
        print(p)
        channel_ls=channel_ls+(p+"\t")
    logging.info("Channel contents: "+channel_ls)
    if handshake():
        canary_id = get_id()
        print("Connection established.")
        logging.info("Connection established.")
        #Main loop; add all constant behaviour here, but be careful for slowdown.
        while True:
            parse_incoming(slack_client.rtm_read())
            time.sleep(0.5) #Avoid DOSing both sides by only checking once every 0.5 seconds.
    else:
        print("Connection failed; see traceback above for details.")
        logging.error("Connection failed.")