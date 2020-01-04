#! /usr/bin/env python3

import libcal

room = libcal.getRoomId("B149A")

libcal.submitBooking(room, "2020-01-07" ,"13:00", 2)