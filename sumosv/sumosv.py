from flask import Flask,jsonify,request
from flask_httpauth import HTTPBasicAuth
from redis import Redis
from rq import Queue
from werkzeug.security import generate_password_hash, check_password_hash
import logging
import os

import sys
sys.path.append("..")

app = Flask(__name__)
auth = HTTPBasicAuth()

flask_host = os.environ.get("FLASK_RUN_HOST", "0.0.0.0")
flask_port = os.environ.get("FLASK_RUN_PORT", 5000)
flask_debug = bool(os.environ.get("FLASK_DEBUG", False))

redis_host = os.environ.get("REDIS_HOST", "localhost")
redis_port = os.environ.get("REDIS_PORT", 6379)


redis_conn = Redis(host=redis_host, port=redis_port)
q = Queue(connection=redis_conn)
logging.basicConfig(filename="sumosv.log",filemode='a',format="%(asctime)s - %(name)s - %(levelname)s: %(message)s",datefmt="%y-%m-%d %H:%M:%S",level=logging.INFO)

users = {
    os.environ.get("SUMO_USER",""): generate_password_hash(os.environ.get("SUMO_PASS",""))
}

@auth.verify_password
def verify_password(username,password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False


#It is assumed that all data is received intact.
@app.route('/healthcheck',methods=['GET'])
def healthcheck():
    return 'OK', 200


#It is assumed that all data is received intact.
@app.route('/alert',methods=['POST'])
@auth.login_required
def getalert():
    logging.info("Post received!")
    #Get message from posted json
    msg = request.get_json(force=True)
    #Enqueue task for pinging slack, pass off to worker queue.
    q.enqueue(slackping,msg)
    #Enqueue other ping functions here when expanding.
    logging.info("Enqueue complete, returning ack.")
    #Return generic ack alongside 200 status.
    return jsonify(status="ACK") #Absolutely broken in unit tests but works fine otherwise.
    

def slackping(data):
    from slackcommon import slackcommon
    #slackcommon.CFGPATH="config/slack_config.ini"
    slackcommon.slack_client = slackcommon.getclient(slackcommon.token)
    print("Handshaking...")
    slackcommon.handshake(slackcommon.slack_client)
    print("Getting config...")
    slackcommon.CONFIG_OPTIONS=slackcommon.getconfig(slackcommon.CONFIG_OPTIONS)
    print("Config attained:")
    print(slackcommon.CONFIG_OPTIONS)
    slackcommon.alert(data)

if __name__ == "__main__":
    app.run(debug=flask_debug, host=flask_host, port=flask_port)