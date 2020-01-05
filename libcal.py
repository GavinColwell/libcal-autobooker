#! /usr/bin/env python3

import requests
import re
import os
from datetime import datetime, timedelta
import json
from bs4 import BeautifulSoup as bs

def getRoomId(room_num):
    with open('roomId.json') as f:
        roomDict = json.load(f)
    return roomDict[room_num]

'''
def getAvailability(date,room='-1'):
    headers = {
        'origin': 'https://uconncalendar.lib.uconn.edu',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'referer': 'https://uconncalendar.lib.uconn.edu/reserve/hbl',
        'authority': 'uconncalendar.lib.uconn.edu',
        'x-requested-with': 'XMLHttpRequest',
        'dnt': '1',
    }

    dateFormat = "%Y-%m-%d"
    startDate = date
    endDate = datetime.strptime(date,dateFormat) + timedelta(days=1)
    endDate = endDate.strftime(dateFormat) 
    data = {
      'lid': '820',
      'gid': '1425',
      'eid': room,
      'start': startDate,
      'end': endDate
    }

    response = requests.post('https://uconncalendar.lib.uconn.edu/spaces/availability/grid', headers=headers, data=data)
    return response.json()
'''
def getAvailability(date):
    url = "https://uconncalendar.lib.uconn.edu/spaces/accessible/ajax/group?prevGroupId=1425&gid=1425&capacity=0&date=" + date

    r = requests.get(url)
    soup = bs(r.text, features="html.parser")
    slots = []
    for slot in soup.select("input"):
        s = {
            "start" : slot.get("data-start"),
            "end" : slot.get("data-end"),
            "itemId" : slot.get("data-eid"),
            "checksum" : slot.get("data-crc")
        }
        slots.append(s)
    return slots

def getDate(days_offset=0):
    
    date = datetime.now() + timedelta(days=days_offset)
    
    dateFormat = "%Y-%m-%d"
    
    dateStr = date.strftime(dateFormat)
    return dateStr

def increaseThirtyMin(start_time):
    hrs, mins = [int(x) for x in start_time.split(":")]

    if mins == 30:
        return str(hrs + 1) + ":00"
    else:
        return str(hrs) + ":30"

def createPayload(room_id, date ,start_time, num_slots):
    avail_slots = getAvailability(date)
    
    payload = {
        'libAuth': 'true',
        'blowAwayCart': 'true'
    }

    i = 0
    t = start_time
    for slot in avail_slots:
        if str(slot["itemId"]) == str(room_id):
            if t in slot["start"]:
                payload["bookings["+str(i)+"][lid]"] = '820'
                payload["bookings["+str(i)+"][gid]"] = '1425'
                payload["bookings["+str(i)+"][eid]"] = str(room_id)
                payload["bookings["+str(i)+"][start]"] = slot["start"]
                payload["bookings["+str(i)+"][end]"] = slot["end"]
                payload["bookings["+str(i)+"][checksum]"] = slot["checksum"]

                i += 1
                t = increaseThirtyMin(t)
                if i == num_slots:
                    return payload
    return payload


def submitBooking(room_id, date, start_time, num_slots):
    headers = {
        'origin': 'https://uconncalendar.lib.uconn.edu',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
       'accept': 'application/json, text/javascript, */*; q=0.01',
        'referer': 'https://uconncalendar.lib.uconn.edu/spaces/accessible/820',
        'authority': 'uconncalendar.lib.uconn.edu',
        'x-requested-with': 'XMLHttpRequest',
        'dnt': '1',
    }

    data = createPayload(room_id, date, start_time, num_slots)

    print(data)
    
    s = requests.session()
    
    response = s.post('https://uconncalendar.lib.uconn.edu/ajax/space/createcart', headers=headers, data=data)
    
    r = response.json()

    print(r)
    
    login_page = s.get(r["redirect"]).text
    
    ## hacky way to get execution_id but I don't feel like using BeautifulSoup
    execution_id = re.search('name="execution" value="(.*)"',login_page).group(0).split('"')[3]
    
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Origin': 'https://login.uconn.edu',
        'Upgrade-Insecure-Requests': '1',
        'DNT': '1',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Referer': 'https://login.uconn.edu/cas/login?service=https%3A%2F%2Flibauth.com%2Flogin%2Fcas',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    params = (
        ('service', 'https://libauth.com/login/cas'),
    )
    
    if not os.environ.get('username') or not os.environ.get('password'):
    	print("Error: include environment variables 'username' and 'password'")
    	exit()
    
    data = {
      'username': os.environ['username'],
      'password': os.environ['password'],
      'execution': execution_id,
      '_eventId': 'submit',
      'geolocation': '',
      'submit': 'Login'
    }
    
    response = s.post('https://login.uconn.edu/cas/login', headers=headers, params=params, data=data)

    headers = {
        'origin': 'https://uconncalendar.lib.uconn.edu',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'referer': 'https://uconncalendar.lib.uconn.edu/equipment/checkout/auth?token=HZBmpY1qL6fegGarZTwatmp5veBEZQVhdGIqNXNC4TNLsvKIxPBKLxohWvX5mnKroQ3vRd4m4QjJeg2CWQTYahuEluDHps9co9fJc1UhKS30jv5XbI41cew8b0gamZjgYROjmpIh58z35lYLneS1PnXTCUEjb7apChft03nxegLo',
        'authority': 'uconncalendar.lib.uconn.edu',
        'x-requested-with': 'XMLHttpRequest',
        'dnt': '1',
    }
    
    data = {
      'forcedEmail': '',
      'returnUrl': '/spaces?lid=820&gid=1425',
      'logoutUrl': 'https://libauth.com/logout.php'
    }
    
    response = s.post('https://uconncalendar.lib.uconn.edu/ajax/equipment/checkout', headers=headers, data=data)
    
    r = response.json()
    print(r)
