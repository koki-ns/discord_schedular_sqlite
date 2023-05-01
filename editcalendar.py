from __future__ import print_function

import datetime
import json
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

class EditCalendar:
    def __init__(self):
        self.creds = self.load_credential()
        try:
            self.service = build('calendar', 'v3', credentials=self.creds)
            self.calendarId = self.load_calendar()
        
        except HttpError as error:
                    print('An error occurred: %s' % error)

    def load_credential(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # トークンがないときの処理、グーグルのログイン画面を呼び出す
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        return creds
    
    def load_calendar(self):
        if os.path.exists("calendar_data.json"):
            with open("calendar_data.json") as file_data:
                calendar = json.load(file_data)
        else:
            calendar = self.create_calendar(self.service)
            with open("calendar_data.json", "w") as file:
                json.dump(calendar, file, indent=4, ensure_ascii=False)
        
        calendarId = calendar["id"]
        
        return calendarId

    def create_calendar(self):
        calendar_list = self.service.calendarList().list().execute()
        for calendar_list_entry in calendar_list['items']:
            if calendar_list_entry['summary'] == '予定管理fromDiscordBot':
                return calendar_list_entry
        
        calendar = {
            'summary': '予定管理fromDiscordBot',
            'timeZone': 'Asia/Tokyo'
        }
        
        created_calendar = self.service.calendars().insert(body=calendar).execute()
        return created_calendar

    def insert_event(self, start, end, summary):
        #カレンダーに追加するイベントのクエリ（json）について調べる
        #終日で追加する
        
        new_event = self.create_event(start, end, summary)
        new_event = self.service.events().insert(calendarId=self.calendarId, body=new_event).execute()
        print("Event created: %s" % (new_event.get('htmlLink')))
        
        
    def create_event(self, start, end, summary):
        # summaryは予定のタイトル
        # start.date, end.dateは"2023-04-06" "2023-04-07"といった形で入力する（終日の場合）
        event = {
            "summary": summary,
            "start": {
                "date":start
                },
            "end": {
                "date":end
                }
        }
        return event
    
    def get_day_events(self, day: datetime.datetime):
        tomorrow = day + datetime.timedelta(days=1)
        timeMin = datetime.datetime.strftime(day, '%Y-%m-%d') + "T00:00:00+09:00"
        timeMax = datetime.datetime.strftime(tomorrow, '%Y-%m-%d') + "T00:00:00+09:00"
        events = self.service.events().list(calendarId=self.calendarId, timeMin=timeMin, timeMax=timeMax).execute()
        #print(events["items"])
        event_list = []
        if events["items"]:
            for event in events["items"]:
                event_list.append(event["summary"])
        #print(event_list)
        return event_list
            
            


def main():
    editCalendar = EditCalendar()
    start = "2023-05-08"
    end = "2023-05-09"
    summary = "スケジュールテスト"
    #editCalendar.insert_event(start, end, summary)
    editCalendar.get_day_events(datetime.datetime(2023, 5, 25))
    
    
    
if __name__ == '__main__':
    main()