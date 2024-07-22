from __future__ import annotations
from pydantic import BaseModel, Field
from uuid import uuid4
from .timedwork import TimedWork
from .schedulable import Schedulable
from datetime import datetime


class Task(TimedWork, Schedulable):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = ''
    
    is_done: bool = False
    is_archived: bool = False
    subtasks: list[Task] = []

    _expanded = True
    _parent = None

    def __repr__(self):
        return f"<Task: {self.name}, Done: {self.is_done}>"

    def _set_parent(self, parent):
        self._parent = parent
        for item in self.subtasks:
            item._set_parent(self)
    
    def save(self):
        if self._parent is not None:
            self._parent.save()
        
    def _toggle_expansion(self):
        _expanded = not _expanded

    def get_all_scheduled_events(self, from_time: datetime, to_time: datetime):
        events = []
        for event in self.events:
            if event.is_within(from_time, to_time):
                events.append(event)
        for task in self.subtasks:
            events.extend(task.get_all_scheduled_events(from_time, to_time))
        return events
    
    def start_work(self):
        super().start_work()
        self.save()

    def end_work(self):
        super().end_work()
        self.save()
        

    

        
