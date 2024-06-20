from nicegui import ui
from abc import ABC, abstractmethod
from gsd.ui import AbstractTheme
from gsd.ui.controls import iconbar_button

class AbstractToolUI(ABC):

    def __init__(self, app):
        self.is_active = False
        self.app = app
        
    def render_menu_item(self):
        color = self.app.theme.text_class_subtle
        if self.is_active:
            color = self.app.theme.text_class_primary


        with ui.item().on_click(self.activate_tool):
            with ui.item_section().props('avatar'):
                ui.icon(self.icon).classes(f'{color}')
            with ui.item_section():
                ui.label(self.name).classes(f'{color}')


        # with self.menu_item.add_slot():
    def render_iconbar_button(self):
        iconbar_button(self.icon, self.activate_tool, self.is_active)


    def activate_tool(self):
        self.app.activate_tool(self)

    def render_sidebar(self):
        pass


    @property
    def icon(self):
        return 'construction'
    
    @property
    def name(self):
        return 'Not Specified'
    
    @property
    def uses_drawer(self) -> bool:
        return False
    
    def render_content(self):
        pass

    @property
    def theme(self) -> AbstractTheme:
        return self.app.theme
    
    