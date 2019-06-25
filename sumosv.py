from flask import Flask,jsonify

@app.route('/alert',methods=['POST'])
def getalert():
    msg =  request.get_json(force=True)
    for(keys,values in msg):
        print(keys)
        print(values)
    return jsonify(status="ACK")