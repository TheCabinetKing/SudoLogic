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


def slackping(data):
    #Watch as the Great and Mysterious Internio quadruples the size of a file with a single line!
    import canary
    canary.getconfig(canary.CONFIG_OPTIONS)
    canary.alert(data)