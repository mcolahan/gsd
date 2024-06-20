from pydantic import BaseModel, Field
from uuid import uuid4

class AbstractTask(BaseModel):
    name: str
    description: str
    id: str = Field(default_factory=lambda: str(uuid4()))
    is_done: bool = False
    _expanded = True
    _parent = None
    

    @property
    def todo_items(self):
        return []

    def _set_parent(self, parent):
        self._parent = parent
        for item in self.todo_items:
            item._set_parent(self)
    
    def save(self):
        if self._parent is not None:
            self._parent.save()
        
    def _toggle_expansion(self):
        _expanded = not _expanded
