from gsd.ui.colors import ColorManager
from nicegui import ui
from typing import Callable
from gsd.model import Task

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
        with ui.button(on_click=on_click).props('flat').classes('m-0 px-3') as btn:
            ui.icon(icon, size='30px').classes(f'py-2 {color}')

    return btn

def extended_input(placeholder="", binded_obj: Task = None, binded_key: str = None) -> ui.input:
    e_input = ui.input(placeholder=placeholder).props('borderless dense w-full')
    
    if binded_obj and binded_key:
        e_input.task = binded_obj
        e_input.bind_value(binded_obj, binded_key)
        e_input.on('blur', lambda e: e.sender.task.save())
        e_input.on('keydown.enter', lambda e: e.sender.task.save())
    
    return e_input

def extended_checkbox(binded_obj: Task, binded_key: str) -> ui.checkbox:
    e_checkbox = ui.checkbox().bind_value(binded_obj, binded_key)
    if binded_obj and binded_key:
        e_checkbox.task = binded_obj
        e_checkbox.bind_value(binded_obj, binded_key)
        e_checkbox.on_value_change(lambda e: e.sender.task.save())
    
    return e_checkbox

def show_hidden_btns(e):
    for btn in e.sender.hover_btns:
        btn.set_visibility(True)

def hide_hidden_btns(e):
    for btn in e.sender.hover_btns:
        btn.set_visibility(False)

def run_method_if_exists(obj, method_name, parent_control=None):
    if hasattr(obj, method_name):
        getattr(obj, method_name)()

    if parent_control:
        parent_control.refresh()

def task_iconbtn(icon: str, on_click: str, render_on_hover_over, task: Task, refreshable, is_hidden=True):
    
    btn = ui.button(icon=icon).props('flat round size=sm').classes('m-0 p-0')
    btn.task = task
    btn.click_method = on_click
    btn.on_click(lambda e: run_method_if_exists(e.sender.task, e.sender.click_method, refreshable))

    if not hasattr(render_on_hover_over, 'hover_btns'):
        render_on_hover_over.hover_btns = []

    render_on_hover_over.hover_btns.append(btn)

    if is_hidden:
        btn.set_visibility(False)
        render_on_hover_over.on('mouseover', lambda e: show_hidden_btns(e))
        render_on_hover_over.on('mouseleave', lambda e: hide_hidden_btns(e))
        
    return btn

