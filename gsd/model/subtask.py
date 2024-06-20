from .abstract_task import AbstractTask
# from .timedwork import TimedWork

class Subtask(AbstractTask):
    def __repr__(self):
        return f"<Subtask: {self.name}>"
    
    @property
    def todo_items(self):
        return []