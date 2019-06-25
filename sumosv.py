from flask import Flask,jsonify,request

app = Flask(__name__)

@app.route('/alert',methods=['POST'])
def getalert():
    #Get message from posted json
    msg =  request.get_json(force=True)
    #Debug outputs to confirm reception
    for keys, values in msg.items():
        print(keys)
        print(values)
    #Return generic ack alongside 200 status.
    return jsonify(status="ACK")