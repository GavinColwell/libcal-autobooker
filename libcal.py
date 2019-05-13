#! /usr/bin/env python3

import requests
import re
import os
from datetime import datetime, timedelta
import json

def getRoomId(room_num):
    with open('roomId.json') as f:
        roomDict = json.load(f)
    return roomDict[room_num]

def getDate(time,duration=1,days=0):
    
    date = datetime.now() + timedelta(days=days)
    
    t = [int(x) for x in time.split(":")]
    
    startDate = date.replace(hour=t[0],minute=t[1])
    
    endDate = startDate + timedelta(hours=duration)
    dateFormat = "%Y-%m-%d %H:%M"
    
    startDate = startDate.strftime(dateFormat)
    endDate = endDate.strftime(dateFormat)
    return [startDate, endDate]

def submitBooking(room_id,start_time,end_time):
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

    data = {
      'libAuth': 'true',
      'blowAwayCart': 'true',
      'bookings[0][lid]': '820',
      'bookings[0][gid]': '1425',
      'bookings[0][eid]': str(room_id),
      'bookings[0][start]': '2019-05-04 7:30',
      'bookings[0][end]': '2019-05-04 8:00',
    }
    
    s = requests.session()
    
    response = s.post('https://uconncalendar.lib.uconn.edu/ajax/space/createcart', headers=headers, data=data)
    
    r = response.json()
    
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
