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
        self._view = "All"


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
        self.create_view(self._view)

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
            self.view_btn('Today', icon='today', on_click=self._change_view)
            self.view_btn('This Week', icon='date_range', on_click=self._change_view)
            ui.separator()
            ui.label("Projects").classes(f'text-lg font-bold p-2 {self.theme.text_class_primary}')
            btn = self.view_btn('All', icon='chevron_right', on_click=self._change_view)
            for proj in self.workspace.projects:
                btn = self.view_btn(proj.name, icon='checklist', project=proj, on_click=self._change_view)

    def view_btn(self, label, icon, project: Project = None, on_click=None):
        btn = ui.button().classes('w-full p-2').props('flat')
        if project is not None:
            btn.context = project
        else:
            btn.context = label
        with btn:
            with ui.row().classes('w-full'):
                ui.icon(icon).classes(f'{self.theme.text_class_primary}')
                ui.label(label).classes(f'{self.theme.text_class_primary}')
        if on_click is not None:
            btn.on_click(on_click)
        return btn
    
    def _change_view(self, e):
        if e.sender.context is not None:
            self._view = e.sender.context

            self.render_content.refresh()
            self.render_sidebar.refresh()


    @ui.refreshable
    def create_view(self, active_view: str):
        with ui.scroll_area().classes('w-full h-full m-0 p-0'):
            with ui.column().classes('w-full h-full m-0 p-0'):
                if active_view == 'All':
                    self.get_all_projects_view()
                elif type(active_view) == Project:
                    self.create_single_project_view(active_view)
                else:
                    pass

    def get_all_projects_view(self):
        with dnd.DnDRow(None).classes('w-full h-full m-4') as projects_row:
            for project in self._projects:
                self.create_project_card(project)
                projects_row.add_drag_target(is_vertical=True)

    def create_single_project_view(self, project: Project):
        with dnd.DnDRow(None).classes('w-full h-full m-4') as projects_row:
            self.create_project_card(project)
            projects_row.add_drag_target(is_vertical=True)


    def create_project_card(self, project: Project):
        card = dnd.task_card(task=project).classes('w-[350px]')
        with card:
            with ui.row().classes('w-full'):
                extended_input(placeholder='Project Name', binded_obj=project, binded_key='name').classes('font-bold text-lg')
                ui.space()

                btn = ui.button(icon='add').props("flat").classes('m-0 p-0').on('click', lambda e: self.on_add_new_task(e.sender.project))
                btn.project = project
                
                with ui.button(icon='more_vert').props("flat").classes('m-0 p-0'):
                    with ui.menu() as menu:
                        cb = ui.checkbox('Show Archived', value=project.render_archived_tasks, on_change=lambda e: self.toggle_render_archived_tasks(e.sender.project))
                        cb.project = project

                        mi = ui.menu_item('Archive', on_click=lambda e: self.on_archive_project(e.sender.project))
                        mi.project = project
                        ui.separator()
                        mi = ui.menu_item('Delete', on_click=lambda e: self.on_delete_project(e.sender.project))
                        mi.project = project

            ui.separator()

            with ui.column().classes('gap-0 w-full m-0 p-0'):
                not_done = [task for task in project.subtasks if not task.is_done and not task.is_archived]
                not_done = sorted(not_done, key=lambda x: x.priority)

                done = [task for task in project.subtasks if task.is_done and not task.is_archived]
                archived = [task for task in project.subtasks if task.is_archived]

                expansion_props = 'dense switch-toggle-side'
                expansion_classes = 'p-0 m-0 mt-2 text-bold w-full gap-0'
                
                with ui.expansion('Todo').props(expansion_props).classes(expansion_classes) as exp:
                    exp.value = True
                    with ui.column().classes('w-full gap-0 m-0 p-0'):                    
                        for task in not_done:
                            self.create_task(task)

                if len(done) > 0:
                    with ui.expansion('Completed').props(expansion_props).classes(expansion_classes):
                        with ui.column().classes('w-full gap-0 m-0 p-0'):  
                            for task in done:
                                self.create_task(task)
                    
                if project.render_archived_tasks and len(archived) > 0:
                    with ui.expansion('Archived').props(expansion_props).classes(expansion_classes):
                        with ui.column().classes('w-full gap-0 m-0 p-0'):  
                            for task in done:
                                self.create_task(task)

    def create_task(self, task: Task):
        priority_color = None
        if task.priority == 1 and not task.is_done:
            priority_color = 'border-red-500'
        elif task.priority == 2 and not task.is_done:
            priority_color = 'border-yellow-500'
        elif task.priority == 3 and not task.is_done:
            priority_color = 'border-blue-500'
        else:
            priority_color = 'border-transparent'
        
        text_color = ''
        if task.is_done:
            text_color = ''
        elif task.is_work_ongoing:
            text_color = 'text-green'
        if task.is_archived:
            text_color = 'text-grey'

        with ui.row().classes('w-full gap-0 border-l-2 ' + priority_color) as row:
            with ui.context_menu() as menu:
                self.get_task_context_menu(task, menu)


            # ui.column().classes('h-full m-0 p-0 bg-orange-500')
            ecb = extended_checkbox(task, 'is_done').classes('m-0 mr-2')
            if task.is_archived:
                ecb.props(add='color="grey"')
                ecb.disable()
            ei = extended_input(placeholder='Task Name', binded_obj=task, binded_key='name').classes(add='w-[200px]').props(add=f'input-class="{text_color}"')
            
            # ui.space()
            # self.get_task_buttons(task, row)




    def add_new_project(self):
        self.workspace.add_project(Project())
        
        self.render_content.refresh()
        self.render_sidebar.refresh()

        ui.notify('New Project Created')

    def on_delete_project(self, project: Project):
        # todo: add confirmation dialog
        self.workspace.remove_project(project)
        self.render_content.refresh()
        self.render_sidebar.refresh()

    def on_archive_project(self, project: Project):
        project.toggle_archived()
        self.render_content.refresh()
        self.render_sidebar.refresh

    def toggle_render_archived_tasks(self, project: Project):
        project.render_archived_tasks = not project.render_archived_tasks
        project.save()
        self.render_content.refresh()


    def on_add_new_task(self, project: Project):
        project.add_subtask(Task())
        self.render_content.refresh()

    def on_delete_task(self, task: Task):
        task._parent.subtasks.remove(task)
        task._parent.save()
        self.render_content.refresh()

    def on_archive_task(self, task: Task):
        task.toggle_archived()
        self.render_content.refresh()

    
    def on_task_show_menu(self, e):
        ui.notify('here')
        task = e.sender.task
        with ui.menu() as menu:
            self.get_task_context_menu(task, menu)


    def get_task_context_menu(self, task: Task, menu):
        ui.label('Priority').classes('m-4 mb-1 text-sm')
        with ui.button_group().classes('m-2'):
            btn = ui.button(icon='priority_high', on_click=lambda e: self._set_task_priority(e.sender.task, 1)).props("flat color='red-500'").classes('text-red-500')
            btn.task = task
            btn = ui.button(icon='arrow_upward', on_click=lambda e: self._set_task_priority(e.sender.task, 2)).props('flat color="yellow-500"')
            btn.task = task
            btn = ui.button(icon='horizontal_rule',on_click=lambda e: self._set_task_priority(e.sender.task, 3)).props('flat color="blue-500"')
            btn.task = task
            btn = ui.button(icon='arrow_downward', on_click=lambda e: self._set_task_priority(e.sender.task, 4)).props('flat color="gray-500"')
            btn.task = task
        
        ui.separator()

        mi = ui.menu_item('Archive', on_click=lambda e: self.on_archive_task(task))
        mi.task = task
        ui.separator()
        mi = ui.menu_item('Delete', on_click=lambda e: self.on_delete_task(task))
        mi.task = task

    def _set_task_priority(self, task: Task, priority: int):
        task.priority = priority
        task.save()
        self.render_content.refresh()

    @ui.refreshable
    def get_task_buttons(self, task: Task, parent):
        with ui.row().classes('items-center gap-1 mt-1'):
            if task.is_work_ongoing:
                task_iconbtn(icon='pause', on_click='end_work', is_hidden=False, render_on_hover_over=parent, task=task, refreshable=self.create_view)
            else:
                task_iconbtn(icon='timer', on_click='start_work', is_hidden=True, render_on_hover_over=parent, task=task, refreshable=self.create_view)

            btn = task_iconbtn(icon='more_vert', on_click=None, is_hidden=True, render_on_hover_over=parent, task=task, refreshable=self.create_view)
            with btn:
                with ui.menu() as menu:
                    self.get_task_context_menu(task, menu)

    
    # def render_task(self, task: Task):
    #     with dnd.card(task):
