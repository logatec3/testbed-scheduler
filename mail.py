#!/usr/bin/python3

import os, sys
import smtplib



class mail:
    _testbed_email = "example@gmail.com"
    _testbed_pwd = "password"

    def __init__(self):
        #self._testbed_email = os.environ.get("EMAIL")
        #self._testbed_pwd = os.environ.get("PASSWORD")
        pass

    def _sendMail(self, receiver, message):
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.ehlo()
            server.login(self._testbed_email, self._testbed_pwd)
            server.sendmail(self._testbed_email, receiver, message)
            server.close()

    def sendReservationSuccess(self, username, user_mail, event):

        msg = """From: LOG-a-TEC testbed
        To: %s <%s>
        Subject: Testbed resource reservation 

        Hello %s!
        Your reservation request for LOG-a-TEC testbed was accepted by the server.
        We kindly ask to wait for admin conformation.

        Technology: %s
        Reserved from: %s
        Until:  %s

        This message was automatically generated by the LOG-a-TEC server - please do not reply.
            
        """%(username, user_mail, username, event["tags"]["radio_type"], event["start"], event["end"])
        self._sendMail(user_mail, msg)

    def sendReservationConfirmed(self, username, user_mail, event):

        msg = """From: LOG-a-TEC testbed
        To: %s <%s>
        Subject: Testbed resource reservation

        Hello %s!
        Your reservation request for LOG-a-TEC testbed was confirmed by the LOG-a-TEC testbed admin.
        For any information please do not hesitate to contact us!

        Technology: %s
        Reserved from: %s
        Until:  %s

        This message was automatically generated by the LOG-a-TEC server - please do not reply.
            
        """%(username, user_mail, username, event["tags"]["radio_type"], event["start"], event["end"])
        self._sendMail(user_mail, msg)

    def sendReservationEnding(self, username, user_mail):

        msg = """From: LOG-a-TEC testbed
        To: %s <%s>
        Subject: Testbed resource reservation

        Hello %s!
        Your reservation for LOG-a-TEC testbed will end at midnight!
        Thank you for using our services.

        This message was automatically generated by the LOG-a-TEC server - please do not reply.
            
        """%(username, user_mail, username)
        self._sendMail(user_mail, msg)
    
