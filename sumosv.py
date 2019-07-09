from flask import Flask,jsonify,request
from flask_httpauth import HTTPBasicAuth
from redis import Redis
from rq import Queue
from werkzeug.security import generate_password_hash, check_password_hash
import logging
import os

app = Flask(__name__)
auth = HTTPBasicAuth()

redis_conn=Redis()
q = Queue(connection=redis_conn)
logging.basicConfig(filename="sumosv.log",filemode='a',format="%(asctime)s - %(name)s - %(levelname)s: %(message)s",datefmt="%y-%m-%d %H:%M:%S",level=logging.INFO)

users = {
    os.environ.get("SUMO_USER"): generate_password_hash(os.environ.get("SUMO_PASS"))
}

@auth.verify_password
def verify_password(username,password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False

#It is assumed that all data is received intact.
@app.route('/alert',methods=['POST'])
@auth.login_required
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
    return jsonify(status="ACK") #Absolutely broken in unit tests but works fine otherwise.
    

def slackping(data):
    import canary
    canary.slack_client = canary.getclient(canary.token)
    print("Handshaking...")
    canary.handshake()
    print("Getting config...")
    canary.CONFIG_OPTIONS=canary.getconfig(canary.CONFIG_OPTIONS)
    print("Config attained:")
    print(canary.CONFIG_OPTIONS)
    canary.alert(data)