import os #Used for token auth.
import time #used only for testing.
from slackclient import SlackClient

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

canary_id = None

#Global constants.
PASSKEY = "217 Lambda" #Passkey to access testing. Used to avoid spam.
channels = [] #List of approved channels for testing.


def parse_incoming(slack_events):
    for event in slack_events:
        if event["type"] == "message" and not subtype in event:
            channel = event["channel"]
            if(channel.startswith('D')):
                msg = event["text"]
                if(msg == "Lambda 217"):
                    slack_client.api_call("chat.postMessage",channel=channel,text="Test addition confirmed. If this is not in a private channel, please immediately deactivate me.")
                    channels.append(channel)
                else:
                    slack_client.api_call("chat.postMessage",channel=channel,text="Invalid passkey. This incident will not be recorded.")
            else:
                print("Invalid channel detected. Response culled.")

def alert():
    #I'm assuming Redis comes in here. Placeholder data in the meantime.
    #while(redis not out of data) needed unless we get an array of dictionaries or something. Which would work, but then needs us to clear sent info twice.
    data = {"AlertThreshold": "Above 90 last 15 minutes", "AlertSource": "Intern Consulting, Co.", "AlertID": "164281", "AlertStatus": "Warning"}
    for approved_channel in channels:
        slack_client.api_call("chat.postMessage",channel=approved_channel,text="Alert from {AlertSource} (status {AlertStatus}).\nReason: {AlertThreshold}\nID: {AlertID}")
    #Empty dictionary in preparation for next in queue. Currently useless.
    data.clear()
#Ensure no accidents cause weird duplicate cases.
if __name__ == "__main__":
    if(slack_client.rtm_connect(with_team_state=False)):
        print("Connection established.")
        #Get bot ID from auth call. This will be useful for mention detection.
        canary_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            message, channel = parse_incoming(slack_client.rtm_read())
            alert()
            time.sleep(20)
    else:
        print("Connection failed; see traceback above for details.")