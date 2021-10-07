#!/usr/bin/python3

import logging
from flask import Flask, render_template, send_from_directory, request
from flask.helpers import url_for


# Logging config
logging.basicConfig(format="%(asctime)s [%(levelname)7s]:[%(name)5s > %(funcName)17s() > %(lineno)3s] - %(message)s", level=logging.DEBUG)#, filename="server.log")
log = logging.getLogger("Server")



# MongoDB config

# Collection name: reservation_events
# 
# Record example:
# {
# '_id': ...
# 'user_name':users{}
# 'start_date': '...',
# 'stop_date' : '...',
# 'start_hour': '...',
# 'stop_hour' : '...',
# 'radio_type': "SRDA"/"SRDB"/...
# 'status' : "pending"/"confirmed"
# }
HOSTNAME = "mongodb://localhost:27017/sms"

#db = MongoClient(HOSTNAME)["sms"]
#users = db["users"]



# Flask config
app = Flask(__name__)

@app.route("/")
def index():
    templateData={"test":"case"}
    return render_template("index.html", **templateData)


# Serve static files 
@app.route("/static/js/<path:path>")
def send_js(path):
    return send_from_directory("static/js/", path)

@app.route("/static/css/<path:path>")
def send_css(path):
    return send_from_directory("static/css/", path)

@app.route("/static/img/<path:path>")
def send_img(path):
    return send_from_directory("static/img/", path)



# TODO test the: request.authorization.username
@app.route("/request-event")
def event():
    # Query arguments are accessable with request.args.get
    #user = request.args.get("user")
    # And headers with:
    #h = request.headres["start"]

    
    if "start" in request.headers:
        return(request.headers["start"])
    else:
        return("NO")

if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)



