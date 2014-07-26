#!/usr/bin/env python
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import RPi.GPIO as GPIO
import time
import urlparse

DOOR_UNLOCK_PIN = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(DOOR_UNLOCK_PIN, GPIO.OUT)


PORT_NUMBER = 8979


class myHandler(BaseHTTPRequestHandler):

    # Handler for the GET requests

    def do_GET(self):

        # Figure out if the user is authorized
        user = self.get_user()
        if user in self.authorized_users():
            self.status = 200  # OK, unlocking
        elif user is None:
            self.status = 400  # bad request, no user provided
        else:
            self.status = 403  # forbidden, user not authorized

        # Build the response
        self.send_response(self.status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        # Send the html message
        if self.status == 200:
            message = "Access Granted."
        elif self.status == 400:
            message = "Just YO."
        elif self.status == 403:
            message = "Access Denied."
        self.wfile.write(
            "<!DOCTYPE html><html><head><title>YO</title><body><h1>YO</h1><p>"
            + message
            + "</p></body></html>")

        # Unlock if necessary
        if self.status == 200:
            self.unlock(5)

        return

    def unlock(self, seconds):
        GPIO.output(DOOR_UNLOCK_PIN, 1)
        time.sleep(seconds)
        GPIO.output(DOOR_UNLOCK_PIN, 0)

    def authorized_users(self):
        # Load list of users authorized to unlock via Yo.
        authorized_users = []
        with open("config/authorized_users.txt") as users:
            authorized_users = [line.rstrip() for line in users]
        return authorized_users

    def get_user(self):
        user = None
        query_parameters = urlparse.parse_qs(
            urlparse.urlparse(self.path).query)
        try:
            usernames = query_parameters['username']
            if len(usernames) == 1:
                user = usernames[0]

        except KeyError:
            pass  # user remains None
        return user

try:
    # Create a web server and define the handler to manage the
    # incoming request
    server = HTTPServer(('', PORT_NUMBER), myHandler)
    print 'Started httpserver on port ', PORT_NUMBER

    # Wait forever for incoming htto requests
    server.serve_forever()

except (KeyboardInterrupt, SystemExit):
    print 'Shutting down.'
    server.socket.close()
    GPIO.cleanup()