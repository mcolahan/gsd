from .abstract_task import AbstractTask
from .timedwork import TimedWork
from .task import Task

class Project(AbstractTask, TimedWork):
    tasks: list[Task] = []


    def __repr__(self):
        return f"<Project: {self.name}>"
    
    @property
    def todo_items(self):
        return self.tasks
    
    def remove_task(self, task):
        if task in self.tasks:
            self.tasks.remove(task)
        self.save()
            
    @property
    def total_work_time(self):
        total_time = super().total_work_time
        for task in self.tasks:
            total_time += task.total_work_time
        return total_time
