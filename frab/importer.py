import re
import sys
import traceback
import requests
import calendar
import pytz
from operator import itemgetter
from datetime import timedelta
from string import split

import dateutil.parser
import defusedxml.ElementTree as ET
import json

def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def get_schedule(url, group):
    
    def load_events(js):
        def to_unixtimestamp(dt):
            dt = dt.astimezone(pytz.utc)
            ts = int(calendar.timegm(dt.timetuple()))
            return ts
        def parse_duration(value):
            h = value / 60
            m = value % 60
            return timedelta(hours=h, minutes=m)

        parsed_events = []
        for event in json.loads(js):
            start = dateutil.parser.parse(event["start_time"]) + timedelta(hours=3)
            duration = parse_duration(event["length"])
            end = start + duration

            parsed_events.append(dict(
                start = start.astimezone(pytz.utc),
                start_str = start.strftime('%H:%M'),
                end_str = end.strftime('%H:%M'),
                start_unix  = to_unixtimestamp(start),
                end_unix = to_unixtimestamp(end),
                duration = int(duration.total_seconds() / 60),
                title = event["title"],
                place = event["room_name"],
                abstract = cleanhtml(event["description"]),
                speakers = split(event["formatted_hosts"], ", "),
                lang = "fi",
                link = "",
                group = "primary",
                id = ""
            ))
        return parsed_events

    r = requests.get(url, timeout=30, stream=True, headers={
        'Accept-Encoding': 'identity'
    })
    schedule = r.raw.read()

    # resp = urllib2.urlopen(url)
    # schedule = resp.read()
    return load_events(schedule)
