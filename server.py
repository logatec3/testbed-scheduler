#!/usr/bin/python3

import logging
from datetime import datetime, timedelta
import dateutil.parser

from pymongo import MongoClient

from flask import Flask, render_template, send_from_directory, request
from flask.helpers import url_for


# Logging config
logging.basicConfig(format="%(asctime)s [%(levelname)7s]:[%(name)5s > %(funcName)17s() > %(lineno)3s] - %(message)s", level=logging.DEBUG)#, filename="server.log")
log = logging.getLogger("Server")



# MongoDB config

# Collection name: reserved_resources
# 
# Record example:
# {
# '_id': ...
# 'user_name':users{}
# 'start': '...',
# 'stop' : '...',
# 'radio_type': "SRDA"/"SRDB"/...
# 'status' : "pending"/"confirmed"
#### Not yet implemented
# 'start_hour': '...',
# 'stop_hour' : '...',
# }
HOSTNAME = "mongodb://localhost:27017/sms"

db = MongoClient(HOSTNAME)["sms"]
users = db["users"]
resource_events = db["reserved_resources"]

# TODO - delete me ---> Dummy event to create collection
admin = users.find_one({"username":"admin"}) #,{"username":1, "type":1, "_id":0})
e_start = datetime(2021, 10, 11).isoformat()
e_end   = datetime(2021, 10, 15).isoformat()

dummy_event = {"user":admin, "start":e_start, "stop":e_end, "radio_type":"SRDA", "status":"confirmed"}
resource_events.insert_one(dummy_event)







# Return a list of reserved events by given type from the database
def getReservedEvents(radio_type):
    events = db["reserved_resources"]
    event_list = []

    for x in events.find({"radio_type":radio_type}):
        event_list.append(x)

    return event_list


# Return True if new_event is not overlaping with others
def isResourceFree(new_event):

    # Get all events
    event_type = new_event.get("tags", {}).get("radio_type")
    events = getReservedEvents(event_type)

    # Add new one
    events.append(new_event)

    # Sort them by start time
    sorted_events = sorted(events, key = lambda d: d["start"])

    # Check for overlaping
    for i in range(1, len(sorted_events)):
        if sorted_events[i - 1]["end"] >= sorted_events[i]["start"]:
            return False

    return True



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


# Handle request for new resource reservation
@app.route("/request-event", methods=["POST"])
def event_request():
    event = request.get_json()

    #1 Check if start in the past
    if event["start"] < datetime.now().isoformat():
        return("Don't fiddle with the past")
    
    #2 Check if start is more than half a year in the future
    halfyear = datetime.now() + timedelta(30 * 6)
    halfyear = halfyear.isoformat()
    if event["start"] > halfyear:
        return("Can't see into the future")
    
    #3 Max 7 days of reservation
    week = dateutil.parser.isoparse(event["start"])
    week = week + timedelta(days=7)
    week = week.isoformat()
    if (event["end"] > week):
        return("Max 7 days")
  
    #4 Check if the event is not overlaping with others
    if (isResourceFree(event)):
        return(event)
    else:
        return("The resources are already reserved for that event")

    # TODO test the: request.authorization.username

if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)
