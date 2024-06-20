from gsd.ui import AbstractToolUI
from nicegui import ui
from gsd.model import *


# class DragAndDropList(ui.list):
#     def __init__(self):
#         super().__init__()

#         # with self.classes('bg-blue-grey-2 w-60 p-4 rounded shadow-2'):
#         #     ui.label(name).classes('text-bold ml-1')
#         self.name = "Hi"
#         self.on('dragover.prevent', self.highlight)
#         self.on('dragleave', self.unhighlight)
#         self.on('drop', self.move_card)
#         self.on_drop = on_drop

#     def highlight(self) -> None:
#         self.classes(remove='bg-blue-grey-2', add='bg-blue-grey-3')

#     def unhighlight(self) -> None:
#         self.classes(remove='bg-blue-grey-3', add='bg-blue-grey-2')

#     def move_card(self) -> None:
#         global dragged  # pylint: disable=global-statement # noqa: PLW0603
#         self.unhighlight()
#         dragged.parent_slot.parent.remove(dragged)
#         with self:
#             card(dragged.item)
#         self.on_drop(dragged.item, self.name)
#         dragged = None


class ProjectTrackerUI(AbstractToolUI):
    def __init__(self, app, workspace):
        super().__init__(app)

        self.workspace = workspace
        self.create_dialogs()

        self._focus_on_new: Task = None  # For quick adding new subtasks to a task
        

    @property
    def icon(self):
        return 'handyman'
    
    @property
    def name(self):
        return 'Projects'
    
    def render_content(self):
    
        with ui.row().classes('p-3'):
            self.load_project_components()
        
        with ui.page_sticky(x_offset=20, y_offset=20):
            btn = ui.button(icon='add', on_click=self.add_new_project).props('fab color=primary')
            btn.tooltip('New Project')

    def create_dialogs(self):
        # with ui.dialog() as new_proj_dialog, ui.card():
        #     input = ui.input('New Project Name: ', placeholder='New Project')
        #     ui.button('Done', on_click=lambda: new_proj_dialog.submit(input.value))
        # self.new_proj_dialog = new_proj_dialog

        with ui.dialog() as remove_proj_dialog, ui.card():
            ui.label('Are you sure you want to delete the project?')
            with ui.row():
                ui.button('Yes', on_click=lambda: remove_proj_dialog.submit(True))
                ui.button('No', on_click=lambda: remove_proj_dialog.submit(False))
        self.remove_proj_dialog = remove_proj_dialog

        with ui.dialog() as remove_subtask_dialog, ui.card():
            label = ui.label('Are you sure you want to delete this subtask?')
            remove_subtask_dialog.label = label
            with ui.row():
                ui.button('Yes', on_click=lambda: remove_subtask_dialog.submit(True))
                ui.button('No', on_click=lambda: remove_subtask_dialog.submit(False))
        self.remove_subtask_dialog = remove_subtask_dialog

        with ui.dialog() as remove_task_dialog, ui.card():
            label = ui.label('Are you sure you want to delete this subtask?')
            remove_task_dialog.label = label
            with ui.row():
                ui.button('Yes', on_click=lambda: remove_task_dialog.submit(True))
                ui.button('No', on_click=lambda: remove_task_dialog.submit(False))
        self.remove_task_dialog = remove_task_dialog

    def create_project_card(self, project: Project) -> None:
        proj_card = ui.card().classes('w-[500px]').style(f"background: {self.theme.bg_secondary}")
        with proj_card:
            with ui.column().classes('w-full h-full'):
                header_grid = ui.grid(columns='1fr auto').classes('w-full')
                with header_grid:
                    ui.input(value=project.name, placeholder='Enter Project Name Here').classes(f'borderless text-h5 {self.theme.text_class_primary}')
                    trash_btn = ui.button(icon='delete', on_click=lambda: self.on_delete_project(project)).props('flat round')#.classes(self.theme.text_class_subtle)
                
                trash_btn.visible = False
                header_grid.on('mouseenter', lambda: trash_btn.set_visibility(True))
                header_grid.on('mouseleave', lambda: trash_btn.set_visibility(False))

                self.render_project_description(project)
                
                # ui.separator()
                with ui.row().classes('w-full'):
                    ui.label('Todo List').classes('text-h7')
                    ui.space()
                    ui.icon('description')

                self.render_project_time(project)
                # with ui.row().classes('w-full'):
                self.render_todo_tree(project)

    def render_project_description(self, project):
        text_input = ui.textarea(
            label='Description: ', 
            value=project.description, 
            placeholder="Enter Project Description Here.", ).props('autogrow borderless').classes(f'w-full')
        text_input.project = project
        text_input.on('keydown.enter', lambda e: self.on_proj_description_enter_press(e))
        text_input.on('blur', lambda e: self.on_project_description_update(e))

    def on_proj_description_enter_press(self, e):
        if ('shiftKey' in e.args.keys() and e.args['shiftKey']):
            text_input = e.sender
            text_input.value = text_input.value[:-1]
            text_input.run_method('blur')

    def on_project_description_update(self, e):
        # ui.notify('On project description update')
        text_input = e.sender
        project = text_input.project
        project.description = text_input.value
        project.save()

        

    async def on_delete_project(self, project) -> None:
        confirmed = await self.remove_proj_dialog
        if confirmed:
            self.workspace.remove_project(project)
            self.load_project_components.refresh()

    # def _render_subtasks(self, task: Task):
    #     subtask_list = ui.list().props('dense w-full')#.style(f'background: {self.theme.bg_primary}')
    #     with subtask_list:
    #         for subtask in task.subtasks:
    #             self._render_subtask(subtask=subtask, task=task, is_new_placeholder=False, parent_list=subtask_list)

    #         # add a placeholder subtask for new subtasks
    #         place_cursor = self._focus_on_new is task
    #         self._render_subtask(subtask=None, task=task, is_new_placeholder=True, parent_list=subtask_list, place_cursor_on_subtask=place_cursor)
    #         if place_cursor:
    #             self._focus_on_new = None

    @ui.refreshable
    def render_project_time(self, project):
        with ui.row().classes('w-full'):
            ui.label(f'Total Working Time / Expected (hrs): {project.total_work_time}/{project.expected_time}')


    @ui.refreshable
    def render_todo_tree(self, project):
        # task_dict = self._get_task_dict(project)
        # tree = ui.tree(task_dict, label_key='id',tick_strategy='leaf', on_tick=lambda e: ui.notify(e.sender))
        # tree.add_slot('header-main', '<span> <strong> {{ props.node.id }} </strong> {{ props.node.completion }}</span>')
        with ui.list().props('dense').classes('w-full') as main_todo_list:
            for task in project.tasks:
                self._render_todo_list_item(task=task, project=project, parent_list=main_todo_list)
        
            place_cursor = self._focus_on_new is project
            self._render_todo_list_item(project=project, is_new_todo=True, parent_list=main_todo_list, place_cursor_on_todo=place_cursor)
            if place_cursor:
                self._focus_on_new = None

        # new_task_input = ui.input(placeholder='New Task').style('margin-left:0px').on('keydown.enter', lambda e: self.on_new_task(e))
        # new_task_input.task = project
            # with ui.expansion(task.name):
            #     for subtask in task.subtasks:
            #         ui.expansion(subtask.name)

    def _render_todo_list_item(self, 
                        project: Project = None,
                        task: Task = None,
                        subtask: Subtask = None, 
                        is_new_todo=False, 
                        parent_list=None,
                        place_cursor_on_todo=False):
        
        is_subtask = subtask is not None
        is_task = not is_new_todo and subtask is None and task is not None
        is_subtask_new_todo = task is not None and is_new_todo
        is_subtask = is_subtask or is_subtask_new_todo

        placeholder_txt = "New Task"
        rendered_item = task
        parent_todo = project
        # print(f'{is_task=}, {is_subtask=}')
        if is_subtask:
            placeholder_txt = "New Subtask"
            rendered_item = subtask
            parent_todo = task
        # print(f"{rendered_item.name=}")
        with ui.item().props('draggable').classes('p-0 m-0 cursor-pointer w-full') as item:
            item.project = project
            item.task = task
            item.subtask = subtask

            item.todo_item = rendered_item
            item.parent_todo = parent_todo

            with ui.context_menu():
                move_up = ui.menu_item('Move up')
                move_up.menu_item = item
                move_up.enabled = (item.todo_item is not None) and parent_todo.todo_items.index(item.todo_item) != 0
                move_up.on_click(lambda e: self._on_move_subtask_up(e.sender.menu_item.todo_item, e.sender.menu_item.parent_todo))

                move_down = ui.menu_item('Move down')
                move_down.menu_item = item
                move_down.enabled = (item.todo_item is not None) and parent_todo.todo_items.index(item.todo_item) != (len(task.subtasks) -  1)
                move_down.on_click(lambda e: self._on_move_todo_down(e.sender.menu_item.todo_item, e.sender.menu_item.parent_todo))

                ui.separator()

                delete = ui.menu_item('Delete')
                delete.enabled = (item.todo_item is not None)
                delete.menu_item = item
                delete.on_click(lambda e: self._on_delete_todo(e.sender.menu_item.todo_item, e.sender.menu_item.parent_todo))


            with ui.item_section().props('avatar'):
                if is_task and len(task.subtasks) > 0:
                    completed_count = sum([subtask.is_done for subtask in task.subtasks])
                    if completed_count < len(task.subtasks):
                        ui.circular_progress(sum([subtask.is_done for subtask in task.subtasks]),
                                            min=0, 
                                            max=len(task.subtasks), 
                                            show_value=False,
                                            size='30px').props('thickness="0.4"')
                    else:
                        cb = ui.checkbox(value=True)
                        cb.enabled = False
                else:
                    cb = ui.checkbox()
                    if is_subtask:
                        cb.classes(add='ml-12')
                    cb.enabled = not is_new_todo
                    if rendered_item is not None:
                        cb.task = rendered_item
                        def _on_val_change(e):
                            e.sender.task.save()
                            self.render_todo_tree.refresh()
                        cb.bind_value(rendered_item, 'is_done').on_value_change(lambda e: _on_val_change(e))

            with ui.item_section() as items_section:
                with ui.grid(columns='1fr auto', rows=1).classes('w-full items-center'):
                    txt_input = ui.input(placeholder=placeholder_txt).props('dense borderless').classes('w-full text-sm')#.style(f'background: {self.theme.negative}')
                    if isinstance(rendered_item, TimedWork):
                        icon = 'timer'
                        icon_color = 'positive'
                        if rendered_item.is_work_ongoing:
                            icon = 'timer_off'
                            icon_color = 'negative'
                        timer_btn = ui.button(icon=icon, color=icon_color).props('flat round').classes('text-xs')
                        timer_btn.timed_item = rendered_item
                        if not rendered_item.is_work_ongoing:
                            timer_btn.visible = False
                            items_section.on('mouseenter', lambda: timer_btn.set_visibility(True))
                            items_section.on('mouseleave', lambda: timer_btn.set_visibility(False))
                            timer_btn.on_click(lambda e: self.on_start_task_timer(e))
                        else:
                            timer_btn.on_click(lambda e: self.on_end_task_timer(e))
                        

                if not is_new_todo:
                    txt_input.todo_item = rendered_item
                    txt_input.bind_value(rendered_item, "name")#.on_value_change(lambda e: e.sender.task.save())
                    txt_input.on('blur', lambda e: e.sender.todo_item.save())
                    txt_input.on('keydown.enter', lambda e: e.sender.todo_item.save())

                else:
                    parent_item = None
                    if task is None:
                        parent_item = project
                    else:
                        parent_item = task
                    txt_input.parent_todo = parent_item

                    txt_input.on('blur', lambda e: self._on_new_todo(e))
                    txt_input.on('keydown.enter', lambda e: self._on_new_todo(e, True))

                if place_cursor_on_todo:
                    txt_input.props(add="autofocus")



        if type(rendered_item) is Task and len(rendered_item.subtasks) > 0:
            for s in rendered_item.subtasks:
                # print(s.name)
                self._render_todo_list_item(subtask=s, task=task, project=project, parent_list=parent_list)
        
            place_cursor = self._focus_on_new is task
            self._render_todo_list_item(task=task, project=project, is_new_todo=True, parent_list=parent_list, place_cursor_on_todo=place_cursor)
            if place_cursor:
                self._focus_on_new = None

            # item.parent = parent
            # item.on('dragover.prevent', lambda e: e.sender.classes(add='bg-blue-grey-3'))
            # item.on('dragleave', lambda e: e.sender.classes(remove='bg-blue-grey-3'))
            # item.on('drop', lambda e: )
            # item.on('dragover.prevent', lambda e: print("Preventing Dragover"))
            # item.on('dragover', lambda e: print(e))


    # def render_task(self, task):
    #     if len(task.subtasks) > 0:
           
                        
    #                 # ui.label(subtask.name)
    #     else:
    #         with ui.row().props('dense draggable') as r:
    #             cb = ui.checkbox().bind_value(task, 'is_done')
    #             txt_input = ui.input(placeholder="New Task").props('dense borderless').classes('w-[70%]')
    #             txt_input.bind_value(task, 'name')
    #         # self._render_subtask(task)
      

            # if is_task and len(task.subtasks) > 0:
            #     with ui.expansion(task.name, value=task._expanded, on_value_change=lambda e: self.toggle_task_expansion(e)).classes('w-full p-0 m-0 h-[20]').props('dense') as expander:#.style(f'background: {self.theme.bg_primary}')
            #         expander.task = task
            #         with expander.add_slot('header'):
            #             with ui.row().classes('w-full items-center') as r:
                            # # icon


                            # # task body
                            # txt_input = ui.input().bind_value(task, 'name').props('dense borderless').classes('w-[70%]')
                            # txt_input.task = task
                            # txt_input.on("click.stop", lambda e: e).on('blur', lambda e: e.sender.task.save())
                            
                            
                            # delete_btn = ui.button( on_click=lambda e: self.on_delete_task(e)).props('flat round icon="delete" color="red" height="15px" width="15px"')
                            # delete_btn.visible = False
                            # r.delete_btn = delete_btn

                            # r.on('mouseenter', lambda e: e.sender.delete_btn.set_visibility(True))
                            # r.on('mouseleave', lambda e: e.sender.delete_btn.set_visibility(False))
                            # delete_btn.task = task

                
                



                            #                    if is_task and len(task.subtasks) > 0:
                            # with ui.list().props('dense w-full') as sub_todo_list:
                            #     for s in task.subtasks:
                            #         self._render_todo_list_item(task=task, project=project, subtask=s, parent_list=sub_todo_list)
                            
                            #     place_cursor = self._focus_on_new is task
                            #     self._render_todo_list_item(task=task, project=project, is_new_todo=True, parent_list=sub_todo_list, place_cursor_on_todo=place_cursor)
                            #     if place_cursor:
                            #         self._focus_on_new = None

    
    

    def _on_move_subtask_up(self, todo_item, parent_todo):

        assert todo_item in parent_todo.todo_items
        i = parent_todo.todo_items.index(todo_item) - 1
        assert i >= 0

        parent_todo.todo_items.remove(todo_item)
        parent_todo.todo_items.insert(i, todo_item)
        parent_todo.save()
        self.render_todo_tree.refresh()

    def _on_move_todo_down(self, todo_item,  parent_todo: Task):

        assert todo_item in parent_todo.todo_items
        i = parent_todo.todo_items.index(todo_item) + 1
        assert i < len(parent_todo.todo_items)

        parent_todo.todo_items.remove(todo_item)
        parent_todo.todo_items.insert(i, todo_item)
        parent_todo.save()
        self.render_todo_tree.refresh()


    async def _on_delete_todo(self, todo_item, parent_todo):
        assert todo_item in parent_todo.todo_items

        self.remove_subtask_dialog.label.text = f'Are you sure you want to delete the item "{todo_item.name}"?'
        confirmed = await self.remove_subtask_dialog
        if confirmed:
            parent_todo.todo_items.remove(todo_item)
            parent_todo.save()
            self.render_todo_tree.refresh()



    def _on_new_todo(self, e, place_cursor_on_new_task=False):
        # ui.notify(f"New Subtask: {e.sender.value}")
        if e.sender.value == "":
            return

        parent_todo = e.sender.parent_todo
        if type(parent_todo) is Project:
            new_todo = Task(name=e.sender.value, description="")
            new_todo._set_parent(parent_todo)
            parent_todo.tasks.append(new_todo)
        else:
            new_todo = Subtask(name=e.sender.value, description="")
            new_todo._set_parent(parent_todo)
            parent_todo.subtasks.append(new_todo)

        if place_cursor_on_new_task:
            self._focus_on_new = parent_todo

        parent_todo.save()
        self.render_todo_tree.refresh()

    def on_new_task(self, e):
        if e.sender.value != "":
            new_task = Task(
                    name=e.sender.value,
                    description=""
                )
            new_task._set_parent(e.sender.task)

            e.sender.task.tasks.append(
                new_task    
            )

            e.sender.task.save()
            self.render_todo_tree.refresh()

    def on_delete_task(self, e):
        task = e.sender.task
        task._parent.remove_task(task)
        self.render_todo_tree.refresh()

    def on_start_task_timer(self, e):
        e.sender.timed_item.start_work()
        e.sender.timed_item.save()
        self.render_todo_tree.refresh()

    def on_end_task_timer(self, e):
        e.sender.timed_item.end_work()
        e.sender.timed_item.save()
        self.render_todo_tree.refresh()

    def toggle_task_expansion(self, e):
        e.sender.task._expanded = e.value
        self.render_todo_tree.refresh()

    def on_task_status_change(self, e):
        # print(e.sender.task)
        e.sender.task.is_done = e.value
        # print(task.is_done)
        e.sender.task.save()
        self.render_todo_tree.refresh()

    # @staticmethod
    # def _get_task_dict(project: Project):
    #     tasks = []
    #     for task in project.tasks:
    #         children = []
    #         completed_children = 0
    #         for subtask in task.subtasks:
    #             children.append({'id': subtask.name, 'header': 'task'})
    #             if subtask.is_done:
    #                 completed_children += 1
    #         completion_status = f' ({completed_children}/{len(children)})'
    #         tasks.append({
    #             'id': task.name,
    #             'children': children,
    #             'header': 'main',
    #             'completion': completion_status
    #         })
    #     return tasks
            
    @ui.refreshable
    def load_project_components(self) -> None:
        for proj in self.workspace.projects:
            self.create_project_card(proj)


    async def add_new_project(self):
        # result = await self.new_proj_dialog
        self.workspace.add_project(
            Project(
                name="",
                description=''
            )
        )
        self.load_project_components.refresh()



