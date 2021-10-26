#!/usr/bin/python3
#
# Class for accessing users database. 


from pymongo import MongoClient

HOSTNAME = "mongodb://localhost:27017/sms"

class testbed_users():

    def __init__(self):
        self.db = MongoClient(HOSTNAME)["sms"]
        self.users = self.db["users"]    

    def _findUser(self, query):
        return self.users.find_one(query)


    def getUserType(self, username):
        user = self._findUser({"username" : username})
        if(user):
            return user["type"]
        else:
            return "unknown"

    def getUserMail(self, username):
        user = self._findUser({"username" : username})
        if(user):
            return user["mail"]
        else:
            return "unknown"

