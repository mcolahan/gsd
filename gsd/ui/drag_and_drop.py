from __future__ import annotations
from typing import Callable, Optional, Protocol
from nicegui import ui
from gsd.model import Task, Project
from enum import IntEnum
from gsd.ui.colors import ColorManager
from abc import ABC


dragged: Optional[card] = None

class DragTarget(ABC):
    def __init__(self, on_drop: callable = None):
        self.on_drop = on_drop
    
    def highlight(self, e) -> None:
        pass
        # print(e)
        # self.classes(remove='bg-blue-grey-2', add='bg-blue-grey-3')

    def unhighlight(self, e) -> None:
        pass
        # print(e)
        # self.classes(remove='bg-blue-grey-3', add='bg-blue-grey-2')

    def move_card(self, e) -> None:
        '''Moves the dragged card to the target column and calls the on_drop callback.'''

        # print(e)

        # global dragged 
        self.unhighlight(e)

    def add_drag_target(self, is_horizontal: bool = False, is_vertical: bool = False):
        if is_horizontal:
            target = ui.row().classes('w-full h-[2px]').style(f'background: {ColorManager.theme.primary}')
        elif is_vertical:
            target = ui.column().classes('w-[2px] h-full').style(f'background: {ColorManager.theme.primary}')

        if target is None:
            return
        
        target.visible = False
        target.on('mouseenter', lambda e: print('mouse entered!'))
        target.on('mouseleave', lambda e: print('mouse left!'))
        
        # dragged.parent_slot.parent.remove(dragged)

        # with self:
        #     card(dragged.item)

        # self.on_drop(dragged.item, self.name)
        # dragged = None





class DnDColumn(ui.column, DragTarget):

    def __init__(self, on_drop: callable = None) -> None:
        super().__init__()
        DragTarget.__init__(self, on_drop)

class DnDRow(ui.row, DragTarget):
    
    def __init__(self, on_drop: callable = None) -> None:
        ui.row.__init__(self)
        DragTarget.__init__(self, on_drop)

        self.on('dragover.prevent', lambda e: self.highlight(e))
        self.on('dragleave', lambda e: self.unhighlight(e))
        self.on('drop', lambda e: self.move_card(e))

        # DragTarget.__init__(self, on_drop)


class card(ui.card):

    def __init__(self) -> None:
        super().__init__()
        self.props(add='draggable flat').classes('cursor-pointer').style(f'background: {ColorManager.theme.bg_secondary}')
        self.on('dragstart', self.handle_dragstart)
        self.on('dragend', self.handle_dragend)
        self.on('dragover.prevent', self.highlight)
        self.on('dragleave', self.unhighlight)

    def handle_dragstart(self) -> None:
        global dragged  # pylint: disable=global-statement # noqa: PLW0603
        self.style(f'background: {ColorManager.theme.bg_secondary}')
        dragged = self

    def handle_dragend(self) -> None:
        self.style(f'background: {ColorManager.theme.bg_secondary}')

    def highlight(self, e) -> None:
        pass
        # print(e)
        # self.classes(remove='bg-blue-grey-2', add='bg-blue-grey-3')

    def unhighlight(self, e) -> None:
        pass
        # print(e)
        # self.classes(remove='bg-blue-grey-3', add='bg-blue-grey-2')

# class DraggableCardContext(IntEnum):
#     Task = 0
#     Project = 1
#     Highlight = 2


class task_card(card):

    def __init__(self, task: Task = None):
        super().__init__()
        self.task = task
        self.is_placeholder = self.task is None

        # self.context = context
        # if type(task) == Project:
        #     self.context = DraggableCardContext.Project

        # with self:
        #     with ui.row():
        #         ui.checkbox().bind_value(task, 'is_done').on_change(lambda e: self.task.save())
        #         ui.input().bind_value(task, 'name').on_change(lambda e: self.task.save())
        #     ui.label(task.name)
            