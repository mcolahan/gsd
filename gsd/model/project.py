
from .task import Task

class Project(Task):
    description: str = ""
    render_archived_tasks: bool = False

    def __repr__(self):
        return f"<Project: {self.name}>"
        



    # def remove_task(self, task):
    #     if task in self.tasks:
    #         self.tasks.remove(task)
    #     self.save()
            
    # @property
    # def total_work_time(self):
    #     total_time = super().total_work_time
    #     for task in self.tasks:
    #         total_time += task.total_work_time
    #     return total_time
