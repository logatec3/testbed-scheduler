#!/usr/bin/python3


# Avtentikacija:
# * session coockie:    request.cookies.get("connect.sid")
# * API Token
    # You can test the: request.authorization.username oz morbt request.headers.authorization
    # V bazi podatkov je ta token shranjen poleg uporabnika (users)

# Na konci me zafrkava to shranjevanje eventov v bazo podatkov
# ogotovu, da bom mogu mal spremenit:

"""
V bazi podatkov nej bo:

user_name:
request_date:
confirmed_by:
event:
    start
    end
    tags:
        status
        radio_type


In na spletni strani nej bo viden sam ta event
"""

import logging
from datetime import date, datetime, timedelta
import dateutil.parser

from pymongo import MongoClient

from flask import Flask, render_template, send_from_directory, jsonify, request
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
e_start = datetime(2021, 10, 6).isoformat()
e_end   = datetime(2021, 10, 7).isoformat()

dummy_event = {"start":e_start, "end":e_end, "tags":{"radio_type":"SRDA", "status":"confirmed"}}
dummy_resource = {"user_name":admin, "request_date":e_start, "confirmed_by":"none", "event":dummy_event}

#resource_events.insert_one(dummy_resource)



# Return a list of reserved events from database
def getReservedEvents():
    events = db["reserved_resources"]
    event_list = []

    for e in events.find():
        event_list.append(e.get("event",{}))

    return event_list




# Return a list of reserved resources by given type from the database
def getReservedResources(radio_type):
    resources = db["reserved_resources"]
    resources_list = []

    for r in resources.find({"event.tags.radio_type":radio_type}):
        resources_list.append(r)

    return resources_list


# Return True if new_event is not overlaping with others
def isResourceFree(new_resource):

    # Get all events
    print(new_resource)
    event_type = new_resource.get("event", {}).get("tags", {}).get("radio_type")
    #event_type = new_resource["event"]["tags"]["radio_type"]
    resources = getReservedResources(event_type)

    # Add new one
    resources.append(new_resource)
    #print(resources)

    # Sort them by start time
    sorted_resources = sorted(resources, key = lambda d: d["event"]["start"])
    print("Sorted resurces ..... ")
    print(sorted_resources)
    # Check for overlaping
    for i in range(1, len(sorted_resources)):
        if sorted_resources[i - 1].get("event",{}).get("end",{}) >= sorted_resources[i].get("event",{}).get("start",{}):
            return False

    return True


def checkRequestedEvent(event):
    
    #1 Check if in the past
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

    # Testing
    #user_token = request.authorization.username
    # print(user_token)
    print("Cookies: ")
    print(request.cookies.get("connect.sid"))

    # If event timings are within desired parameters
    resp = checkRequestedEvent(event)

    # If resources are free
    if(resp == "success"):  
        now = datetime.now().isoformat()
        resource = {"user_name":"nekUser", "request_date":now, "confirmed_by": "none", "event": event}
        
        if (isResourceFree(resource)):

            print("----Tip resource variable")
            print(type(resource))

            db["reserved_resources"].insert_one(resource)
            for i in resource_events.find():
                print(i)
        else:
            resp = "The resources are already reserved for that event"
    print("response is " + resp)
    
    return jsonify(
        response_message = resp,
        #response_event = event,
    )

@app.route("/update", methods=["POST"])
def update_calendar():
    r = request.get_json()
    print(r)

    events = getReservedEvents()

    return jsonify(events)


if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)