#!/usr/bin/python3

import logging
import subprocess

from pymongo import MongoClient

from flask import Flask, render_template, send_from_directory, jsonify, request
from flask.helpers import url_for

from testbed_resources import testbed_resources
tr = testbed_resources()

from testbed_users import testbed_users
tu = testbed_users()

# ------------------------------------------------------------------------------------------
# Logging config
# ------------------------------------------------------------------------------------------
logging.basicConfig(format="%(asctime)s [%(levelname)7s]:[%(name)5s > %(funcName)17s() > %(lineno)3s] - %(message)s", level=logging.INFO, filename="scheduler.log")
log = logging.getLogger("Server")

# ------------------------------------------------------------------------------------------
# Function to send mail in a subprocess
# ------------------------------------------------------------------------------------------
def sendMail(type, event):
    res_owner = tr.getResourceOwner(event)
    res_owner_mail = tu.getUserMail(res_owner)
    res_start = event["start"]
    res_end = event["end"]
    res_type = event["tags.radio_type"]
    subprocess.Popen(["python3", "testbed_mail.py", type, res_owner, res_owner_mail, res_start, res_end, res_type])


# ------------------------------------------------------------------------------------------
# Flask config
# ------------------------------------------------------------------------------------------
app = Flask(__name__, static_url_path="", static_folder="static", template_folder="templates")

@app.route("/")
def index():
    # Finta u levu: ime shrani v span z id-jom username in za admina vrni drugi JS fajl
    user = request.args.get("u")
    log.info(user + " accessed the scheduler app.")

    user_type = tu.getUserType(user)

    if(user_type == "unknown"):
        return "<h1>Unauthorized access</h1>"
    else:
        templateData = {"username":user, "option":user_type}
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


# Update reserved resource events from the database
@app.route("/update", methods=["POST"])
def update_calendar():
    log.info("Update events from database")

    req = request.get_json()
    # TODO: you can use req to cleanup old events (req = {today:"..."})

    events = tr.getEventList()

    return jsonify(events)


# Handle request for new resource reservation
@app.route("/event-request", methods = ["POST"])
def event_request():
    event = request.get_json()
    username = event.pop("user")
    usermail = tu.getUserMail(username)

    if(usermail == "unknown"):
        return jsonify(msg = "Sorry..your username does not exist")

    # Check requested event
    resp = tr.isResourceFree(event)
    if(resp == "success"):
        tr.storeResource(event, username)
        sendMail("reservation_success", event)

    log.info("Request got response: " + resp)
    return jsonify(msg = resp)


# Handle admin modifications
@app.route("/event-modify", methods = ["POST"])
def event_confirm():
    event = request.get_json()
    modifier = event.pop("user")
    action = event.pop("action")

    if(tu.getUserType(modifier) != "admin"):
        return jsonify(msg = "User is not authorized")
        
    if (action == "delete"):
        resp = tr.deleteResource(event)
    elif (action == "confirm"):
        resp = tr.confirmResource(event, modifier)
        sendMail("reservation_confirmed", event)

    log.info("Admin " + modifier + action + "ed event with ID " + event["id"])
    return jsonify(msg = resp)





#def admin_rights(func):
#    @wraps(func)
#    def check_admin(*args, **kwargs):
#        # Check if user has admin rights
#        user = db["users"].find_one({"username":username})
#        if(user):
#            if(user["type"] != "admin"):
#                return jsonify(msg = "User is not authorized")
#        return func(*args, **kwargs)
#    return check_admin


if __name__ == "__main__":
    app.run(host="localhost", port=8002, debug=True)