#! /usr/bin/env python3

import libcal

room = libcal.getRoomId("1-104C")

dates = libcal.getDate("00:30", 2, 2)

print(dates)

#libcal.submitBooking(room, dates[0], dates[1])