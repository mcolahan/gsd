from .abstract_tool_ui import AbstractToolUI
from gsd.model import *
from nicegui import ui
from . import drag_and_drop as dnd
from dataclasses import dataclass
from gsd.ui.controls import extended_input, extended_checkbox, task_iconbtn


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
    
    @ui.refreshable
    def render_content(self):
        self.get_project_view('All')

        with ui.page_sticky(x_offset=18, y_offset=18):

            with ui.element('q-fab').props('icon=add color=primary direction=up'):
                ui.element('q-fab-action').props('icon=work color=primary') \
                    .on('click', lambda: self.add_new_project())
                # ui.element('q-fab-action').props('icon=sailing color=green-5') \
                #     .on('click', lambda: ui.notify('boat'))
                # ui.element('q-fab-action').props('icon=rocket color=green-5') \
                #     .on('click', lambda: ui.notify('rocket'))
            
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

    @ui.refreshable
    def render_sidebar(self):
        
        with ui.column().classes('w-full h-full p-2'):
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


    @ui.refreshable
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
        card = dnd.task_card(task=project).classes('w-[350px]')
        with card:
            with ui.row().classes('w-full'):
                extended_input(placeholder='Project Name', binded_obj=project, binded_key='name').classes('font-bold text-lg')
                ui.space()
                with ui.button(icon='more_vert').props("flat").classes('m-0 p-0'):
                    with ui.menu() as menu:
                        ui.menu_item('Archive')
                        ui.separator()
                        ui.menu_item('Delete')

            with ui.column().classes('gap-0'):
                for task in project.subtasks:
                    self.create_task(task)

    def create_task(self, task: Task):
        with ui.row().classes('items-center w-full') as row:
            extended_checkbox(task, 'is_done')
            extended_input(placeholder='Task Name', binded_obj=task, binded_key='name').classes('font-semibold')
            
            self.get_task_buttons(task, row)

    def add_new_project(self):
        self.workspace.add_project(Project())
        
        self.render_content.refresh()
        self.render_sidebar.refresh()

        ui.notify('New Project Created')

    @ui.refreshable
    def get_task_buttons(self, task: Task, parent):
        with ui.row().classes('items-center gap-1'):
            if task.is_work_ongoing:
                task_iconbtn(icon='pause', on_click='end_work', is_hidden=False, render_on_hover_over=parent, task=task, refreshable=self.get_project_view)
            else:
                task_iconbtn(icon='timer', on_click='start_work', is_hidden=True, render_on_hover_over=parent, task=task, refreshable=self.get_project_view)


    
    # def render_task(self, task: Task):
    #     with dnd.card(task):
