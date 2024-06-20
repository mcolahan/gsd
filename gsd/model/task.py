from .abstract_task import AbstractTask
from .timedwork import TimedWork
from .subtask import Subtask
import datetime

class Task(AbstractTask, TimedWork):
    subtasks: list[Subtask] = []
    _parent = None


    def __repr__(self):
        return f"<Task: {self.name}>"
    
    @property
    def todo_items(self):
        return self.subtasks
    
    def remove_task(self, task):
        if task in self.subtasks:
            self.subtasks.remove(task)
        self.save()
