import time #Used for sleep to avoid network strain.
import logging

import sys
sys.path.append("..")
from slackcommon import slackcommon

CONFIG_OPTIONS = slackcommon.CONFIG_OPTIONS
slack_client = slackcommon.slack_client
logging.basicConfig(filename="canary.log",filemode='a',format="%(asctime)s - %(name)s - %(levelname)s: %(message)s",datefmt="%y-%m-%d %H:%M:%S",level=logging.INFO)

#Add channel to authorised channel list.
def addchannel(channel):
    if channel not in CONFIG_OPTIONS["channels"]:
        CONFIG_OPTIONS["channels"].append(channel)
        logging.info("Added channel {0} to alert list".format(channel))
        slackcommon.setconfig(CONFIG_OPTIONS)

#Remove channel from authorised channel list.
def rmchannel(channel):
    if channel in CONFIG_OPTIONS["channels"]:
        CONFIG_OPTIONS["channels"].remove(channel)
        logging.info("Removed channel {0} from alert list".format(channel))
        slackcommon.setconfig(CONFIG_OPTIONS)

#Helper function for "help" command; commands can be added in the cmdlist variables. Remember that the existing config would override it!
def sendhelp(channel):
    slackcommon.sendmsg(channel,"All commands are directly messaged, or prefaced with a mention.")
    msgout = "Direct commands:\n"
    for command in CONFIG_OPTIONS["cmdlist_dir"]:
        msgout = msgout + ("\t*"+command+"*"+" - "+CONFIG_OPTIONS["cmdlist_dir"][command]+"\n")
    slackcommon.sendmsg(channel, msgout)
    msgout="Mention commands:\n"
    for command in CONFIG_OPTIONS["cmdlist_men"]:
        msgout = msgout + ("\t*"+command+"*"+" - "+CONFIG_OPTIONS["cmdlist_men"][command]+"\n")
    slackcommon.sendmsg(channel, msgout)
    logging.info("Help message sent to channel {0}".format(channel))

def dmhandler(channel,msg):
    #Subscription
    if(msg.startswith("subscribe")):
        addchannel(channel)
        slackcommon.sendmsg(channel,"Subscription confirmed.")
        return
    #Unsubscription
    if(msg.startswith("unsubscribe")):
        rmchannel(channel)
        slackcommon.sendmsg(channel,"Delisting successful.")
        return
    #Remember to document all added commands in *both* help responses!
    if(msg.startswith("help")):
        sendhelp(channel)

def mentionhandler(channel,msg):
    #Add current channel to alert list.
    if(msg.startswith("list")):
        addchannel(channel)
        slackcommon.sendmsg(channel,"Confirmed; channel added to alert list.")
        return
    #Remove current channel from alert list.
    if(msg.startswith("delist")):
        rmchannel(channel)
        slackcommon.sendmsg(channel,"Delisting successful.")
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

#Used to assign canary_id.
def get_id():
    return slack_client.api_call("auth.test")["user_id"]

#Ensure only one message listener active.
if __name__ == "__main__":
    slack_client = slackcommon.getclient(slackcommon.token)
    slackcommon.slack_client = slack_client
    CONFIG_OPTIONS = slackcommon.getconfig(CONFIG_OPTIONS)
    print("Config attained. Channel contents: ")
    channel_ls="" #Log output variable, no use after for loop's log update.
    for p in CONFIG_OPTIONS["channels"]:
        print(p)
        channel_ls=channel_ls+(p+"\t")
    logging.info("Channel contents: "+channel_ls)
    if slackcommon.handshake(slack_client):
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