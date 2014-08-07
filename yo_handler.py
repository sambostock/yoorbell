#!/usr/bin/env python
'''Uses Yothenticator to trigger door unlock upon successful authentication.'''

from yothenticator import YothenticatorServer as YoServer
from yothenticator import YothenticatorRequestHandler as YoHandler
import RPi.GPIO as GPIO
import time
import yaml

# Load config file
config = None
with open("config.yaml") as config_file:
    config = yaml.load(config_file)

# Get constants from config
API_TOKEN = config["api-token"]
AUTHORIZED_USERS = config["users"]["authorized"]
DOOR_UNLOCK_PIN = config["pins"]["door"]
PORT_NUMBER = config["port"]

GPIO.setmode(GPIO.BCM)
GPIO.setup(DOOR_UNLOCK_PIN, GPIO.OUT)


def unlock(self, seconds):
    '''Trigger the GPIO pin to unlock the door for the given number of seconds.
    '''
    GPIO.output(DOOR_UNLOCK_PIN, 1)
    time.sleep(seconds)
    GPIO.output(DOOR_UNLOCK_PIN, 0)

try:
    # Create a web server and define the handler to manage the
    # incoming request
    server = YoServer(('', PORT_NUMBER), YoHandler, AUTHORIZED_USERS,
                      action_success=unlock(5))
    print 'Started door unlock Yothenticator Server on port', PORT_NUMBER

    # Wait forever for incoming htto requests
    server.serve_forever()

except (KeyboardInterrupt, SystemExit):
    print 'Shutting down.'
    server.socket.close()
    GPIO.cleanup()
