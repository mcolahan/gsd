from gsd.ui import AbstractToolUI
from gsd.model import *
from nicegui import ui
import asyncio

import sys, os, pathlib

class NotesUI(AbstractToolUI):

    def __init__(self, app, workspace: Workspace):
        super().__init__(app)
        self.workspace = workspace
        self.directory_configured, self.dir_msg = self.check_notes_directory()

        self.open_tabs = []
        # self.create_dialogs()

        self.file_ext_icons = {
            'md': 'south',
            'txt': 'description'
        }


    @property
    def icon(self):
        return 'history_edu'

    @property
    def name(self):
        return "Notes"
    
    @property
    def uses_drawer(self):
        return True
    
    def render_content(self):

        if not self.directory_configured:
            with ui.column().classes('m-10'):
                ui.label(self.dir_msg)
                ui.button('Select Directory', icon='folder_open')
            return
        
        self.render_tabs()

    @ui.refreshable
    def render_tabs(self):
        with ui.column().classes('w-full h-full gap-0'):
            with ui.tabs().props('dense no-caps indicator-color="primary" align="left"').classes('w-full p-0 m-0').style(f"background: {self.theme.bg_secondary}") as tabs:
                for file_path in self.workspace.open_notes:
                    fpath = pathlib.Path(file_path)
                    with ui.tab(fpath.name,"") as tab:
                        with ui.row().classes('justify-center gap-0 border-x-1') as r:
                            ui.icon(self.file_ext_icons['md']).classes('pt-1')
                            ui.label(fpath.name).classes('text-xs mx-2 pt-1')
                            close_btn = ui.button(icon='close', color=None).props('flat size="xs" round').classes(f'text-xs text-slate-400')
                            close_btn.visible = False
                            close_btn.file_path = file_path
                            close_btn.on_click(lambda e: self.close_note(e))
                            tab.close_btn = close_btn
                            tab.on('mouseover', lambda e: e.sender.close_btn.set_visibility(True))
                            tab.on('mouseleave', lambda e: e.sender.close_btn.set_visibility(False))

            with ui.tab_panels(tabs).classes('w-full h-full p-0 m-0').props('transition-prev="jump-left" transition-next="jump-right"').style(f'background: {self.theme.bg_secondary}'): # jump-right, jump-left
                for file_path in self.workspace.open_notes:
                    fpath = pathlib.Path(file_path)
                    with ui.tab_panel(fpath.name).classes('w-full h-full p-0 m-0'):
                        with open(file_path, 'r') as f:
                            file_text = f.read()
                        line_count = len(file_text.splitlines())
                        
                        tab_splitter = ui.splitter().classes('w-full h-full')
                        with tab_splitter.before:
                            # with ui.scroll_area().classes('w-full h-full p-0 m-0 pr-2').style(f'background: {self.theme.accent}'):
                            txt_area = ui.textarea().props('borderless autogrow').classes('h-full w-full font-mono px-4')#.style(f'background: {self.theme.primary}')
                            txt_area.value = file_text

                        with tab_splitter.after:
                            md_displayer = ui.markdown(file_text, extras=['fenced-code-blocks','tables','latex']).classes('h-full w-full px-4')


            if self.workspace.selected_notes_index > 0:
                selected_tab_name = pathlib.Path(self.workspace.open_notes[self.workspace.selected_notes_index]).name
                # self.render_selected_tab()
                tabs.set_value(selected_tab_name)


    # def render_selected_tab(self):
    #     with ui.tab
    #     ui.label(self.workspace.open_notes[self.workspace.selected_notes_index])



    def render_sidebar(self):
        is_configured, msg = self.check_notes_directory()
        if not is_configured:
            return 
        
        self.get_notes_tree()
        



    def check_notes_directory(self):
        if self.workspace.notes_directory == "":
            msg = "A notes directory has not been configured for this workspace.\nWould you like to create one?"
        elif not os.path.exists(self.workspace.notes_directory):
            msg = "The currently specified notes directory does not exist.\nWould you like to specify a new one?"
        else:
            # await True
            return True, None
        return False, msg

    
    def get_notes_tree(self):
        notes_path = pathlib.Path(self.workspace.notes_directory)
        notes_contents = self.get_directory_contents(notes_path)
        with ui.column().classes('h-full w-full space-y-0').style('gap: 0.1rem'):
            with ui.row().classes('w-full').style(f'background: {self.theme.bg_secondary}'):
                ui.label(notes_path.name.upper()).classes('text-bold m-2 ml-3')
            tree = ui.tree(notes_contents, label_key='label').classes('w-full dense px-3 m-0')
            tree.on_select(self._on_path_selected)

    def _on_path_selected(self, e):
        raw_path = e.value
        if raw_path is None:
            return
        path = pathlib.Path(raw_path)
        if path.is_dir():
            return
        assert path.exists()
        
        if raw_path in self.workspace.open_notes:
            # change tab to the selected file
            selected_index = self.workspace.open_notes.index(raw_path)
            self.workspace.selected_notes_index = selected_index
            self.workspace.save()
            self.render_tabs.refresh()

            return
        
        else:
            self.workspace.open_notes.append(raw_path)
            self.workspace.selected_notes_index = self.workspace.open_notes.index(raw_path)
            self.workspace.save()
            self.render_tabs.refresh()

            return

    def close_note(self, e):
        file_path = e.sender.file_path
        if file_path in self.workspace.open_notes:
            i = self.workspace.selected_notes_index
            if self.workspace.open_notes.index(file_path) == i:
                i -= 1

            self.workspace.open_notes.remove(file_path)

            if i > len(self.workspace.open_notes) - 1:
                i = len(self.workspace.open_notes) - 1

            self.workspace.selected_notes_index = i
            self.workspace.save()
            self.render_tabs.refresh()
            


    
    @staticmethod
    def get_directory_contents(path: pathlib.Path):
        _, folders, files = list(next(os.walk(path)))
        contents = []
        for folder in folders:
            folder_path = path.joinpath(folder)
            assert folder_path.exists()
            folder_contents = NotesUI.get_directory_contents(folder_path)
            contents.append(
                {'id': str(path.joinpath(folder).absolute()),
                 'label': folder,
                'children': folder_contents}
            )
        for f in files:
            contents.append({
                'id': str(path.joinpath(f).absolute()),
                'label': f,
                })

        return contents
