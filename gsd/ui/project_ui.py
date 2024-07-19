from .abstract_tool_ui import AbstractToolUI
from gsd.model import *
from nicegui import ui
from . import drag_and_drop as dnd
from dataclasses import dataclass
from gsd.ui.controls import extended_input


class ProjectUI(AbstractToolUI):

    def __init__(self, app, workspace: Workspace):
        super().__init__(app)
        self.workspace = workspace

    @property
    def _projects(self):
        return self.workspace.projects
    
    @property
    def icon(self):
        return 'checklist'
    
    @property
    def name(self):
        return "Projects"
    
    @property
    def uses_drawer(self):
        return True
    
    def render_content(self):
        self.get_project_view('All')
        
        # def handle_drop(todo: ToDo, location: str):
        #     ui.notify(f'"{todo.title}" is now in {location}')


        # with ui.row():
        #     with dnd.column('Next', on_drop=handle_drop):
        #         dnd.card(ToDo('Simplify Layouting'))
        #         dnd.card(ToDo('Provide Deployment'))
        #     with dnd.column('Doing', on_drop=handle_drop):
        #         dnd.card(ToDo('Improve Documentation'))
        #     with dnd.column('Done', on_drop=handle_drop):
        #         dnd.card(ToDo('Invent NiceGUI'))
        #         dnd.card(ToDo('Test in own Projects'))
        #         dnd.card(ToDo('Publish as Open Source'))
        #         dnd.card(ToDo('Release Native-Mode'))

    def render_sidebar(self):
        
        with ui.column().classes('w-[220px] h-full p-2'):
            self.view_btn('Today', icon='today')
            self.view_btn('This Week', icon='date_range')
            ui.separator()
            ui.label("Projects").classes(f'text-lg font-bold p-2 {self.theme.text_class_primary}')
            self.view_btn('All', icon='chevron_right')
            for proj in self.workspace.projects:
                self.view_btn(proj.name, icon='checklist')

    def view_btn(self, label, icon):
        btn = ui.button().classes('w-full p-2').props('flat')
        with btn:
            with ui.row().classes('w-full'):
                ui.icon(icon).classes(f'{self.theme.text_class_primary}')
                ui.label(label).classes(f'{self.theme.text_class_primary}')
        return btn


    def get_project_view(self, active_view: str):
        if active_view == 'All':
            self.get_all_projects_view()
        else:
            pass

    def get_all_projects_view(self):
        with dnd.DnDRow(None).classes('w-full h-full m-4') as projects_row:
            for project in self._projects:
                self.create_project_card(project)
                projects_row.add_drag_target(is_vertical=True)


    def create_project_card(self, project: Project):
        card = dnd.task_card(task=project).classes('w-[250px]')
        with card:
            extended_input(placeholder='Project Name', binded_obj=project, binded_key='name').classes('font-bold text-lg')


    
    # def render_task(self, task: Task):
    #     with dnd.card(task):
