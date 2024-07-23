from nicegui import ui, context, app
from gsd.ui.colors import *
from gsd.utils.observer import ColorListener
from gsd.model import Workspace
from gsd.ui import AbstractToolUI, NotesUI, GoalsUI, CalendarUI, ProjectUI
from gsd.ui.controls import iconbar_button
from gsd.user_preferences import UserPreferences
import webview
import asyncio
import tempfile
import uuid


class App(ColorListener):
    def __init__(self):
        self.user_prefs = UserPreferences.load()
        if len(self.user_prefs.recent_workspaces) > 0:
            self.workspace_path = self.user_prefs.recent_workspaces[0]
            self.workspace = Workspace.load(self.workspace_path)
            self.is_temp_workspace = False
        else:
            self.workspace_path = tempfile.gettempdir() + '\\' + str(uuid.uuid4()) + Workspace.workspace_ext()
            self.workspace = Workspace()
            self.workspace.save(self.workspace_path)
            self.is_temp_workspace = True
                              
        context.client.content.classes('h-[100vh] w-[100vw] m-0 p-0 flex')#.style("height: 100%")
        ui.add_head_html('<style>.q-textarea.flex-grow .q-field__control { height: 100% }</style>')

        self.tools: list[AbstractToolUI] = [
            ProjectUI(self, self.workspace),
            NotesUI(self, self.workspace),
            GoalsUI(self, self.workspace),
            CalendarUI(self, self.workspace),
        ]
        self.tools[self.user_prefs.selected_tool].is_active = True

        ColorManager.instance().register_listener(self)
        if self.user_prefs.dark_mode:
            ColorManager.set_mode('dark')
        else:
            ColorManager.set_mode('light')
        self.theme = ColorManager.theme

        ui.page_title('GSD')
            
        

    def update_color_theme(self, theme):
        self.theme = theme
        ui.colors(
            primary = self.theme.primary,
            secondary = self.theme.secondary,
            accent = theme.accent,
            dark = theme.dark,
            positive = theme.positive,
            negative=theme.negative,
            info=theme.info,
            warning=theme.warning
        )
        self.user_prefs.dark_mode = ColorManager.is_dark_mode()
        self.user_prefs.save()
        self.create_layout.refresh()

    # def set_color_theme(self):
    #     theme = self.theme
    #     ui.colors(
    #         primary = self.theme.primary,
    #         secondary = self.theme.secondary,
    #         accent = theme.accent,
    #         dark = theme.dark,
    #         positive = theme.positive,
    #         negative=theme.negative,
    #         info=theme.info,
    #         warning=theme.warning
    #     )

    def update_dark_mode(self, dark_mode=False):
        if ColorManager.is_dark_mode != dark_mode:
            mode = 'dark'
            if not dark_mode:
                mode = 'light'
            ColorManager.set_mode(mode)
        

        
    @property
    def active_tool(self) -> AbstractToolUI:
        for tool in self.tools:
            if tool.is_active:
                return tool
        return None
        
    def activate_tool(self, tool:AbstractToolUI):
        assert tool is not None, 'Tool is nothing.'
        assert tool in self.tools, 'Tool to be activated is not in the tool list.'
        
        if tool is not self.active_tool:
            self.active_tool.is_active = False
            tool.is_active = True

            if tool.uses_drawer:
                self.sidebar_splitter.set_value(10)
                self.sidebar_splitter.enable()
                self.render_sidebar()
            else:
                self.sidebar_splitter.set_value(0)
                self.sidebar_splitter.disable()

            self.render_iconbar()
            self.render_content()

            self.user_prefs.selected_tool = self.tools.index(tool)
            self.user_prefs.save()

    def initialize(self):
        self.create_layout()


    @ui.refreshable
    def create_layout(self):
        # self.header = ui.header()
        with ui.column().classes('h-full w-full m-0 p-0 gap-0').style(f'background: {self.theme.bg_primary}'):

            with ui.row().classes('w-full h-[40px] m-0 p-0 pl-2 items-center gap-0 pywebview-drag-region').style(f'background: {self.theme.bg_secondary}'):
                button_classes = 'h-full'
                button_props = 'flat size=xs'
                button_color = 'text-neutral-400'
            
                ui.label('🚀').classes('text-lg mx-2')
                with ui.button().classes('h-full m-0 p-0 px-4').props('flat square size=md'):
                    ui.label('File').classes(button_color + ' text-md p-0 m-0')
                    with ui.menu().props('auto-close').classes('w-auto'):
                        ui.menu_item('New', on_click=lambda e: self.on_new_workspace())
                        ui.menu_item('Open', on_click=lambda e: self.on_open_workspace())
                        ui.menu_item('Save As', on_click=lambda e: self.on_save_as())
                        ui.separator()
                        ui.menu_item('Close')

                ui.space()
                ui.label('Get Sh!t Done').classes('font-semibold').style(f'color: {self.theme.text_primary}')

                ui.space()
                
                button_classes = 'h-full m-0 p-0 px-4'
                button_props = 'flat size=xs'
                button_color = 'text-neutral-400'

                with ui.button().classes(button_classes).props(button_props):
                    ui.icon('horizontal_rule').classes(button_color)
                with ui.button().classes(button_classes).props(button_props):
                    ui.icon('crop_square').classes(button_color)
                with ui.button().classes(button_classes).props(button_props).on_click(lambda e: self.close()):
                    ui.icon('close').classes(button_color)

            self.main_grid = ui.grid(columns="auto 1fr", rows=1).classes('h-full w-full m-0 p-0 gap-0').style(f'background: {self.theme.bg_primary}')
        
            with self.main_grid:
                self.icon_bar = ui.column().classes('h-full gap-0').style(f'background: {self.theme.bg_secondary}')
                self.render_iconbar()
                
                self.sidebar_splitter = ui.splitter().classes('h-full w-full m-0 p-0 b-1').style(f'background: {self.theme.bg_primary}')
                self.render_sidebar()

                self.render_content()

    def render_iconbar(self):
        self.icon_bar.clear()
        with self.icon_bar:
            for tool in self.tools:
                tool.render_iconbar_button()

            ui.space()
            btn = iconbar_button('settings', None)
            with btn:
                with ui.menu().props('auto-close').classes('w-auto'):
                    with ui.menu_item():
                        ui.switch('Dark Mode', value=ColorManager.is_dark_mode(), on_change=lambda e: self.update_dark_mode(e.value))
        
    def render_sidebar(self):
        if len(self.sidebar_splitter.before.children) > 0:
            self.sidebar_splitter.before.children.clear()

        if self.active_tool.uses_drawer:
            self.sidebar_splitter.enable()
            self.sidebar_splitter.set_value(12)
            with self.sidebar_splitter.before:
                self.active_tool.render_sidebar()
        else:
            self.sidebar_splitter.set_value(0)
            self.sidebar_splitter.disable()

    def render_content(self):
        self.sidebar_splitter.after.children.clear()
        with self.sidebar_splitter.after:
            self.active_tool.render_content()


    def on_new_workspace(self):
        ui.notify("Creating a new Workspace!")

    def on_open_workspace(self):
        ui.notify("Opening an Existing Workspace")


    def run(self):
        self.create_layout()
        start_args = {
            'title': 'Get Sh!t Done',
            'resizable': True,
            'width': 1500,
            'height': 1000,
            'easy_drag': False,
        }

        app.native.window_args = start_args
        self.app = ui.run(favicon='🚀', native=True, frameless=True,)

    def close(self):
        self.workspace.save()
        app.native.main_window.destroy()
        quit()


    async def on_new_workspace(self):
        result = await app.native.main_window.create_file_dialog(
                    webview.SAVE_DIALOG,
                    file_types=('JSON Files (*.json)', 'All files (*.*)'),
                    save_filename='workspace.json')

        if result is None or len(result) == 0:
            return

        workspace_file = result

        workspace = Workspace()
        workspace.save(workspace_file)
        
        self.workspace = workspace
        self.workspace_path = workspace_file
        self.user_prefs.add_recent_workspace(workspace_file)

        self.refresh_app()

    async def on_save_as(self):
        result = await app.native.main_window.create_file_dialog(
            webview.SAVE_DIALOG,
            file_types=('JSON Files (*.json)', 'All files (*.*)'),
            save_filename='workspace.json')
        
        if result is None or len(result) == 0:
            return
        workspace_file = result
        self.workspace.save(workspace_file)
        self.workspace_path = workspace_file
        self.is_temp_workspace = False
        self.user_prefs.add_recent_workspace(workspace_file)

    async def on_open_workspace(self):
        result = await app.native.main_window.create_file_dialog(
            webview.OPEN_DIALOG,
            file_types=('JSON Files (*.json)', 'All files (*.*)'),
            allow_multiple=False)

        if result is None or len(result) == 0:
            return
        
        workspace_file = result[0]
        workspace = Workspace.load(workspace_file)
        self.workspace = workspace
        self.workspace_path = workspace_file
        self.refresh_app()
        self.user_prefs.add_recent_workspace(workspace_file)
        
    def refresh_app(self):
        for tool in self.tools:
            tool.workspace = self.workspace
        self.create_layout.refresh()
        




if __name__ in {"__main__", "__mp_main__"}:
    my_app = App()
    my_app.run()
    