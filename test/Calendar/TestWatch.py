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
    page_token = None
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

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime') #Ex:2021-02-13T03:30:00-08:00 (date)T(Time-Timezone)
        end = event['end'].get('dateTime')
        #start = event['start'].get('dateTime', event['start'].get('date'))
        print(event['summary'])
        print(start)
        print(end)

    #Make a time object then of curret system
    now = datetime.datetime.now().isoformat(timespec='seconds') #Ex:2021-02-09T02:26:50
    print(now)

if __name__ == '__main__':
    main()