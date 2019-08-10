import urllib.request
import json
import os

#Basic auth user+pass
sumo_auth = os.environ.get("SUMO_BASICAUTH")
sumo_auth = "Basic "+sumo_auth

#Optional incorrect user+pass for testing
#sumo_auth="Basic FRTFRL"

#Body to post
body = {"AlertThreshold": "0 last 10 minutes", "AlertSource": "Intern Consulting, Co.", "AlertID": "189224"}

#Target URL; remember to use flask with the "-p 1337" argument! That's mostly to test that non-default ports work, as you need port 80 for production.
tgtsv = "http://127.0.0.1:1337/alert"

req=urllib.request.Request(tgtsv)
req.add_header('Content-Type','application/json; charset=utf-8')
req.add_header("Authorization",sumo_auth)


tosend=json.dumps(body)
tosendasbytes=tosend.encode('utf-8')
req.add_header('Content-Length',len(tosendasbytes))
response=urllib.request.urlopen(req,tosendasbytes)
print(response)