#!/usr/bin/python3
#
# Class for testbed resource management. 
# On the frontend only the event part of the document is seen (for any kind of user type).
#
# Resource document template:
# ----------------------+-----------------------------------------------------------------------------------------------
# owner                 | Resource owner username (coresponds with users database)
# request_date          | Date when request was made
# confirmed_by          | Username of the admin that confirmed the request
# event:                | 
#     start             | Start of the reserved event (ISO format)
#     end               | End of the reserved event (ISO format)
#     tags:             | 
#         status        | "pending" -> waiting for user conf / "confirmed"
#         radio_type    | Type of testbed resources (SRDA / SRDB / LPWA / UWB / BLE)
# ----------------------+-----------------------------------------------------------------------------------------------


from datetime import datetime, timedelta
import dateutil.parser

from pymongo import MongoClient

import logging

LOGGING_LEVEL = logging.INFO

HOSTNAME = "mongodb://localhost:27017/sms"

RESERVATION_MAX_DAYS = 7            # Reservation possible for max 7 days
RESERVATION_FUTURE_DEPTH = 6        # Only half year in advanced

class testbed_resources():

    def __init__(self):
        self.db = MongoClient(HOSTNAME)["sms"]
        self.resources = self.db["reserved_resources"]    
        self.log = logging.getLogger("Resources")
        self.log.setLevel(LOGGING_LEVEL)

    def _findResource(self, query):
        return self.resources.find_one(query)

    def _storeResource(self, res):
        self.resources.insert_one(res)

    def _updateResource(self, query, new_value):
        self.resources.update_one(query, new_value)

    def _deleteResource(self, query):
        self.resources.delete_one(query)


    # ------------------------------------------------------------------------------------------------------------------
    # Resource manipulation (admin access)
    
    def deleteResource(self, event):
        query = {"event.id" : event["id"]}
        self._deleteResource(query)

        return "success"

    def confirmResource(self, event, confirmed_by):
        query = {"event.id" : event["id"]}
        conformation = {"$set": {"event.tags.status" : "confirmed"}}
        conf_by = conf_by = {"$set": {"confirmed_by" : confirmed_by}}

        self._updateResource(query, conformation)
        self._updateResource(query, conf_by)

        return "success"

    def getResourceOwner(self, event):
        resource = self._findResource({"event.id" : event["id"]})
        return resource["owner"]


    # Resource manipulation (client access)
    def storeResource(self, event, owner):
        now = datetime.now().isoformat()
        resource = {
            "owner" : owner,
            "request_date" : now,
            "confirmed_by" : "none",
            "event" : event
        }
        self._storeResource(resource)
        
        return "success"

    def isResourceFree(self, event):
        #1 Check if event is in the past
        if event["start"] < datetime.now().isoformat():
            return "Can't reserve resources in the past"
        
        #2 Check if start is more than half a year in the future
        future = datetime.now() + timedelta(30 * RESERVATION_FUTURE_DEPTH)
        future = future.isoformat()
        if event["start"] > future:
            return ("Reservation possible max %i months in advanced"%{RESERVATION_FUTURE_DEPTH})
        
        #3 Max 7 days of reservation
        day = dateutil.parser.isoparse(event["start"])
        day = day + timedelta(days = RESERVATION_MAX_DAYS)
        day = day.isoformat()
        if (event["end"] > day):
            return ("Reservation possible for max %i days"%{RESERVATION_MAX_DAYS})

        if(not self.isEventFree(event)):
            return "The resources are already reserved for chosen period!"

        return "success"

   
    # ------------------------------------------------------------------------------------------------------------------
    # Event manipulation
    
    def getEventList(self):
        event_list = []

        for r in self.resources.find():
            event_list.append(r.get("event", {}))

        return event_list


    def getEventListByType(self, radio_type):
        resources_list = []

        for r in self.resources.find({"event.tags.radio_type" : radio_type}):
            resources_list.append(r.get("event", {}))

        return resources_list


    def getEventListByOwner(self, owner):
        resources_list = []

        for r in self.resources.find({"owner" : owner}):
            resources_list.append(r.get("event", {}))

        return resources_list

    def printEvents(self):
        events = self.getEventList()
        for e in events:
            self.log.info(e)


    def isEventFree(self, event):
        type = event.get("event", {}).get("tags", {}).get("radio_type")

        events = self.getEventListByType(type)
        events.append(event)

        sorted_events = sorted(events, key = lambda d: d["event"]["start"])

        # Check for overlaping
        for i in range(1, len(sorted_events)):
            if sorted_events[i - 1].get("event",{}).get("end",{}) > sorted_events[i].get("event",{}).get("start",{}):
                return False

        return True


    
    

