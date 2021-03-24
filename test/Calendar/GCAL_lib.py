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

class Gcal:
    def __init__(self):
        #Setup class var
        self.creds = None
        self.service = None
        self.ID = None
        self.workFlag = False
        self.recEvent = {}
        self.token = None
        self.flow = None
        self.page_token = None
        #Build the service function
        self.setup()

    def setup(self):
        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next event on the user's calendar.
        This also builds out the service object which allows the all of api Google
        calendar API methods to be used.
        """
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time. ONLY NEED To AUTH Once
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as self.token:
                self.creds = pickle.load(self.token)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                self.flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = self.flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as self.token:
                pickle.dump(self.creds, self.token)

        self.service = build('calendar', 'v3', credentials=self.creds)

    def nextEvent(self, systemDate):
        """ This is get function to retrieve the next future event based on the given time 
        that was pass into the class function
        """
        while True:
            calendar_list = self.service.calendarList().list(pageToken=self.page_token).execute()
            #print(calendar_list) This will print the entire payload
            for calendar_list_entry in calendar_list['items']:
                if (calendar_list_entry['summary'] == 'Work'): # Check if the correct calender even exist in the calendar pool
                    workFlag = True
                    ID = (calendar_list_entry['id'])
                    print(ID)
                    print("The user calendar 'Work' exists")
            self.page_token = calendar_list.get('nextPageToken')
            if not self.page_token:
                break

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = self.service.events().list(calendarId=ID, timeMin=now,
                                            maxResults=20, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print("No upcoming events founds.")
            self.recEvent = None
        for event in events:
            start = event['start'].get('dateTime') #Ex:2021-02-13T03:30:00-08:00 (date)T(Time-Timezone)
            splDate = start.split("T")
            stime = splDate[1].split("-")
            rstime = stime[0].rsplit(":", 1)
            end = event['end'].get('dateTime')
            end1 = end.split("T")
            endtime = end1[1].split("-")
            rendtime = endtime[0].rsplit(":", 1)
            title = (event['summary'])
            #The first events of the same date will be added to the table
            if systemDate == splDate[0]:
                if ("Meeting") in title:
                    self.recEvent = {'Title' : title, 'Date': splDate[0], 'Start' : rstime[0], 'End' : rendtime[0]}
                    break
                else:
                    self.recEvent = None
            self.workFlag = False
            del now
        return (self.recEvent)