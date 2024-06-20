from gsd.ui.colors import ColorManager
from nicegui import ui
from typing import Callable

def get_theme():
    return ColorManager.theme

def iconbar_button(icon: str, on_click: Callable, is_active:bool=False):
    theme = get_theme()
    color = theme.text_class_subtle
    if is_active:
        color = theme.text_class_primary

    blaze_color = ColorManager.theme.bg_secondary
    if is_active:
        blaze_color = ColorManager.theme.primary
    with ui.row().classes('gap-0 border-l-2').style(f'border-color: {blaze_color}'):
        with ui.button(on_click=on_click).props('flat').classes('m-0') as btn:
            ui.icon(icon, size='30px').classes(f'py-2 {color}')

    return btn