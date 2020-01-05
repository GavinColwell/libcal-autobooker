#! /usr/bin/env python3

import libcal, json

date = libcal.getDate(days_offset=3)

with open("settings.json") as json_file:
    settings = json.load(json_file)
    room = settings["roomId"]
    startTime = settings["startTime"]
    numSlots = settings["numSlots"]

    libcal.submitBooking(room,date,startTime,numSlots)
