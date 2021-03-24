from __future__ import print_function
import datetime
import pickle
import time
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time. ONLY NEED To AUTH Once
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    ID = None
    workFlag = False
    counter = 1
    page_token = None
    recEvent = {}
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        #print(calendar_list) This will print the entire payload
        for calendar_list_entry in calendar_list['items']:
            if (calendar_list_entry['summary'] == 'Work'): # Check if the correct calender even exist in the calendar pool
                workFlag = True
                ID = (calendar_list_entry['id'])
                print(ID)
                print("The user calendar 'Work' exists")
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId=ID, timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    #Make a time object then of curret system
    now = datetime.datetime.now().isoformat(timespec='seconds') #Ex:2021-02-09T02:26:50
    nowDate = now.split("T")
    print(nowDate[0])
    print("Current system time ", now)

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime') #Ex:2021-02-13T03:30:00-08:00 (date)T(Time-Timezone)
        splDate = start.split("T")
        stime = splDate[1].split("-")
        end = event['end'].get('dateTime')
        end1= end.split("T")
        endtime= end1[1].split("-")
        title = (event['summary'])
        #Only same day events will be added to the table
        if nowDate[0] == splDate[0]:
            recEvent[counter] = {'Title' : title, 'Date': splDate[0], 'Start' : stime[0], 'End' : endtime[0]}
            #start = event['start'].get('dateTime', event['start'].get('date'))
            #print(event['summary'])
            #print(start)
            #print(end)
            counter+=1
    #print ((recEvent[1]['Start'])>((recEvent[2]['Start'])))#Use this to compare off ACSII
    print(recEvent)
    print(len(recEvent))#React to instant changes


    

if __name__ == '__main__':
    main()

###This is the attempt result 3 mins before event ended
"""
Getting the upcoming 10 events
2021-02-11
Current system time  2021-02-11T02:02:06
False
{1: {'Title': 'check_event', 'Date': '2021-02-11', 'Start': '02:00:00', 'End': '02:05:00'}, 2: {'Title': 'Get force entry detection working', 'Date': '2021-02-11', 'Start': '11:30:00', 'End': '12:30:00'}, 3: {'Title': 'SMS feature', 'Date': '2021-02-11', 'Start': '15:00:00', 'End': '16:00:00'}, 4: {'Title': 'Should be event 3', 'Date': '2021-02-11', 'Start': '18:30:00', 'End': '19:30:00'}}
4
"""

###This is called right 7 seconds after the event ended
"""
Getting the upcoming 10 events
2021-02-11
Current system time  2021-02-11T02:05:07
False
{1: {'Title': 'Get force entry detection working', 'Date': '2021-02-11', 'Start': '11:30:00', 'End': '12:30:00'}, 2: {'Title': 'SMS feature', 'Date': '2021-02-11', 'Start': '15:00:00', 'End': '16:00:00'}, 3: {'Title': 'Should be event 3', 'Date': '2021-02-11', 'Start': '18:30:00', 'End': '19:30:00'}}
3
"""
