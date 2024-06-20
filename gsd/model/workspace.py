import pathlib

from pydantic import BaseModel
from .project import Project
from .task import Task


class Workspace(BaseModel):
    name: str
    projects: list[Project] = []
    misc_tasks: list[Task] = []
    notes_directory: str = ""
    open_notes: list[str] = []
    selected_notes_index: int = 0

    _file_path: str = None
    
    def __repr__(self):
        return f"<Workspace: {self.name}>"
    
    def save(self, file_path: str = None):
        if file_path is None:
            file_path = self._file_path
        path = pathlib.Path(file_path)
        if not path.parent.exists():
            raise ValueError("Parent path does not exist!")

        with open(path, 'w') as f:
            f.write(self.model_dump_json(indent=2))
        
    
    @staticmethod
    def load(file_path):
        path = pathlib.Path(file_path)
        assert path.exists(), "Path does not exist."

        with open(path, 'r') as f:
            json_txt = f.read()

        ws = Workspace.model_validate_json(json_txt)
        for proj in ws.projects:
            proj._set_parent(ws)
        ws._file_path = file_path
        return ws
    
    def add_project(self, proj):
        self.projects.append(proj)
        self.save()

    def remove_project(self, proj):
        if proj in self.projects:
            self.projects.remove(proj)

        self.save()




