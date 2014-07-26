#!/usr/bin/env python
import RPi.GPIO as GPIO
import datetime
import time
from yoapi import yo

# Load API Token from file
API_TOKEN = None
with open("config/api_token.txt") as api_token:
    API_TOKEN = api_token.read().rstrip()

# Function to read in users to YO
def get_users_to_notify():
    with open("config/notify_users.txt") as users:
        return [line.rstrip() for line in users]

# Initalize Yo client
yo_client = yo.api(API_TOKEN)

# Function to Yo all users found in the notify file
def yo():
    # Since buzzes are not a super regular occurence, the overhead from reloading the list of users is negligable.
    for user in get_users_to_notify():
        yo_client.yo(user)

# Pin to listen for buzz on
BUZZ_INPUT_PIN = 24

# Config GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZ_INPUT_PIN, GPIO.IN)

# Function to get timestamp string
def timestamp():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Function to confirm edge is valid, and not from a bounce or floating signal
def confirm_buzz(pin):
    count = 0
    for i in range(20):
        time.sleep(0.005)  # sleep 5ms between samples
        count += 1 if GPIO.input(pin) else -1
    if count > 0:
        handle_buzz()

# Function to Yo and log a confirmed buzz
def handle_buzz():
    yo()
    print "A buzz buzzed @ " + timestamp()


# Register callback on rising edge
GPIO.add_event_detect(BUZZ_INPUT_PIN, GPIO.RISING, callback=confirm_buzz, bouncetime=200)


# Loop forever, letting threaded callback handle buzzes
print "Listening for buzz... (" + timestamp() + ")"
try:
    while True:
        pass
except (KeyboardInterrupt, SystemExit):
    print "Stopping @ " + timestamp()

# Cleanup before exiting
GPIO.cleanup()