from nicegui import ui, context
from gsd.ui.colors import *
from gsd.utils.observer import ColorListener
from gsd.model import Workspace
from gsd.ui import AbstractToolUI, NotesUI, GoalsUI, CalendarUI, ProjectUI
from gsd.ui.controls import iconbar_button
from gsd.user_preferences import UserPreferences


class App(ColorListener):
    def __init__(self):
        self.workspace_path = 'test_workspace.json'
        self.workspace = Workspace.load(self.workspace_path)
        self.user_prefs = UserPreferences.load()

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
        ui.run()




if __name__ in {"__main__", "__mp_main__"}:
    app = App()
    app.run()
    