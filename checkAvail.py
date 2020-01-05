#! /usr/bin/env python3

import libcal

room = libcal.getRoomId("B149A")

date = "2019-12-07"

availabilities = libcal.getAvailability(date)

for slot in availabilities:
    if slot["itemId"] == room:
        print(slot)
