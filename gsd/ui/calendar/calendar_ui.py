from gsd.ui import AbstractToolUI
from nicegui import ui
from .fullcalendar import FullCalendar
from datetime import datetime

class CalendarUI(AbstractToolUI):

    def __init__(self, app, workspace):
        super().__init__(app)
        self.workspace = workspace


    @property
    def icon(self):
        return 'calendar_month'
    
    @property
    def name(self):
        return "Calendar"
    
    def render_content(self):
        options = {
            'initialView': 'dayGridMonth',
            'headerToolbar': {'left': 'prev,next today', 'center': 'title', 'right': 'dayGridMonth,timeGridWeek,timeGridDay'},
            # 'footerToolbar': {'right': 'prev,next today'},
            # 'slotMinTime': '05:00:00',
            # 'slotMaxTime': '22:00:00',
            # 'allDaySlot': False,
            'timeZone': 'local',
            'events': [
                {
                    'title': 'Math',
                    'start': datetime.now().strftime(r'%Y-%m-%d') + ' 08:00:00',
                    'end': datetime.now().strftime(r'%Y-%m-%d') + ' 10:00:00',
                    'color': 'red',
                },
                {
                    'title': 'Physics',
                    'start': datetime.now().strftime(r'%Y-%m-%d') + ' 10:00:00',
                    'end': datetime.now().strftime(r'%Y-%m-%d') + ' 12:00:00',
                    'color': 'green',
                },
                {
                    'title': 'Chemistry',
                    'start': datetime.now().strftime(r'%Y-%m-%d') + ' 13:00:00',
                    'end': datetime.now().strftime(r'%Y-%m-%d') + ' 15:00:00',
                    'color': 'blue',
                },
                {
                    'title': 'Biology',
                    'start': datetime.now().strftime(r'%Y-%m-%d') + ' 15:00:00',
                    'end': datetime.now().strftime(r'%Y-%m-%d') + ' 17:00:00',
                    'color': 'orange',
                },
            ],
        }
        FullCalendar(options, None).classes('h-full w-full p-6')
    