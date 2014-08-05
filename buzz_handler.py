#!/usr/bin/env python
import RPi.GPIO as GPIO
import datetime
import time
from yoapi import yo
import yaml

# Load config file
config = None
with open("config.yaml") as config_file:
    config = yaml.load(config_file)

# Get constants from config
API_TOKEN = config["api-token"]
USERS_TO_NOTIFY = config["users"]["notify"]
BUZZ_INPUT_PIN = config["pins"]["buzz"]
BOUNCETIME = config["calibration"]["bouncetime"]
SAMPLES = config["calibration"]["samples"]
DELAY = config["calibration"]["delay"] / 1000.0 # ms -> sec

# Initalize Yo client
yo_client = yo.api(API_TOKEN)

# Function to Yo all users found in the config file
def yo():
    for user in USERS_TO_NOTIFY:
        yo_client.yo(user)

# Config GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZ_INPUT_PIN, GPIO.IN)

# Function to get timestamp string
def timestamp():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Function to confirm edge is valid, and not from a bounce or floating signal
def confirm_buzz(pin):
    count = 0
    for i in range(SAMPLES):
        time.sleep(DELAY)  # sleep 5ms between samples
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