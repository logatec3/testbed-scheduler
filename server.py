#!/usr/bin/python3

import logging
from flask import Flask, render_template, send_from_directory
from flask.helpers import url_for


# Logging config
logging.basicConfig(format="%(asctime)s [%(levelname)7s]:[%(name)5s > %(funcName)17s() > %(lineno)3s] - %(message)s", level=logging.DEBUG)#, filename="server.log")
log = logging.getLogger("Server")

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