#!/usr/bin/python3


# Avtentikacija:
# * session coockie:    request.cookies.get("connect.sid")
# * API Token
    # You can test the: request.authorization.username oz morbt request.headers.authorization
    # V bazi podatkov je ta token shranjen poleg uporabnika (users)

"""
Database document example (only event is seen on the frontend)

user_name:
request_date:
confirmed_by:
event:
    start
    end
    tags:
        status
        radio_type
"""

import logging
from datetime import date, datetime, timedelta
import dateutil.parser

from pymongo import MongoClient

from flask import Flask, render_template, send_from_directory, jsonify, request
from flask.helpers import url_for


# Logging config
logging.basicConfig(format="%(asctime)s [%(levelname)7s]:[%(name)5s > %(funcName)17s() > %(lineno)3s] - %(message)s", level=logging.INFO)#, filename="server.log")
log = logging.getLogger("Server")


# MongoDB config
HOSTNAME = "mongodb://localhost:27017/sms"

db = MongoClient(HOSTNAME)["sms"]
users = db["users"]
reserved_resources = db["reserved_resources"]


# Dummy event to create collection
"""
admin = users.find_one({"username":"admin"}) #,{"username":1, "type":1, "_id":0})
e_start = datetime(2021, 10, 6).isoformat()
e_end   = datetime(2021, 10, 7).isoformat()

dummy_event = {"start":e_start, "end":e_end, "tags":{"radio_type":"SRDA", "status":"confirmed"}}
dummy_resource = {"user_name":admin, "request_date":e_start, "confirmed_by":"none", "event":dummy_event}

resource_events.insert_one(dummy_resource)
"""


# Return a list of reserved events from database
def getReservedEvents():
    events = db["reserved_resources"]
    event_list = []

    for e in events.find():
        event_list.append(e.get("event",{}))

    return event_list


# Return a list of reserved resources by given type from the database
def getReservedResources(radio_type):
    log.debug("Get " + radio_type + " reserved resources")
    resources = db["reserved_resources"]
    resources_list = []

    for r in resources.find({"event.tags.radio_type":radio_type}):
        resources_list.append(r)

    return resources_list

# Return True if new_event is not overlaping with others
def isResourceFree(new_resource):

    # Get all events
    log.info("Is resource free")
    log.debug(new_resource)

    event_type = new_resource.get("event", {}).get("tags", {}).get("radio_type")
    resources = getReservedResources(event_type)
    resources.append(new_resource)

    # Sort them by start time
    sorted_resources = sorted(resources, key = lambda d: d["event"]["start"])

    # Check for overlaping
    for i in range(1, len(sorted_resources)):
        if sorted_resources[i - 1].get("event",{}).get("end",{}) > sorted_resources[i].get("event",{}).get("start",{}):
            return False

    return True

# Check if event is in considarable limits
# Messages that are returned will be visible on the frontend modal.
def checkRequestedEvent(event):
    #1 Check if event is in the past
    if event["start"] < datetime.now().isoformat():
        return "Can't reserve resources in the past"
    
    #2 Check if start is more than half a year in the future
    halfyear = datetime.now() + timedelta(30 * 6)
    halfyear = halfyear.isoformat()
    if event["start"] > halfyear:
        return "Reservation possible max 6 months in advanced"
    
    #3 Max 7 days of reservation
    week = dateutil.parser.isoparse(event["start"])
    week = week + timedelta(days=7)
    week = week.isoformat()
    if (event["end"] > week):
        return "Reservation possible for max 7 days"

    return "success"




# ------------------------------------------------------------------------------------------
# Flask config
# ------------------------------------------------------------------------------------------
app = Flask(__name__, static_url_path="", static_folder="static", template_folder="templates")

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


# Update reserved resources from the database
@app.route("/update", methods=["POST"])
def update_calendar():
    log.info("Update events from database")

    req = request.get_json()
    # TODO: you can use req for deleting old events (req = {today:"..."})

    events = getReservedEvents()

    return jsonify(events)


# Handle request for new resource reservation
@app.route("/request-event", methods=["POST"])
def event_request():
    event = request.get_json()

    # Testing
    #user_token = request.authorization.username
    # print(user_token)
    print("Cookies: ")
    print(request.cookies.get("connect.sid"))

    # If event timings are within desired parameters
    resp = checkRequestedEvent(event)

    if(resp == "success"):
        user = "NekUser"
        now = datetime.now().isoformat()
        resource = {"user_name":user, "request_date":now, "confirmed_by": "none", "event": event}
        
        if (isResourceFree(resource)):
            # Store new request into database
            db["reserved_resources"].insert_one(resource)
        else:
            resp = "The resources are already reserved for chosen period!"

    log.info("Request got response: " + resp)
    
    return jsonify(
        response_message = resp,
        #response_event = event,
    )


if __name__ == "__main__":
    app.run(host="localhost", port=8002)