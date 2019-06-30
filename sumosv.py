from flask import Flask,jsonify,request
from redis import Redis
from rq import Queue

app = Flask(__name__)

redis_conn=Redis()
q = Queue(connection=redis_conn)

@app.route('/alert',methods=['POST'])
def getalert():
    #Get message from posted json
    msg =  request.get_json(force=True)
    #Debug outputs to confirm reception
    q.enqueue(slackping,msg)
    #Return generic ack alongside 200 status.
    return jsonify(status="ACK")


def slackping(data):
    #Watch as the Great and Mysterious Internio quadruples the size of a file with a single line!
    import canary
    canary.slack_client = canary.getclient(canary.token)
    print("Handshaking...")
    canary.handshake()
    print("Getting config...")
    canary.CONFIG_OPTIONS=canary.getconfig(canary.CONFIG_OPTIONS)
    print("Config attained:")
    print(canary.CONFIG_OPTIONS)
    canary.alert(data)