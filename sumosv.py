from flask import Flask,jsonify,request
from redis import Redis
from rq import Queue
import logging

app = Flask(__name__)

redis_conn=Redis()
q = Queue(connection=redis_conn)
logging.basicConfig(filename="sumosv.log",filemode='a',format="%(asctime)s - %(name)s - %(levelname)s: %(message)s",datefmt="%y-%m-%d %H:%M:%S",level=logging.INFO)

#It is assumed that all data is received intact.
@app.route('/alert',methods=['POST'])
def getalert():
    logging.info("Post received!")
    #Get message from posted json
    msg = request.get_json(force=True)
    logging.info("JSON acquired.")
    #Enqueue task for pinging slack, pass off to worker queue.
    q.enqueue(slackping,msg)
    #Enqueue other ping functions here when expanding.
    logging.info("Enqueue complete, returning ack.")
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