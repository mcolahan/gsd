from gsd.ui import AbstractToolUI
from nicegui import ui

class GoalsUI(AbstractToolUI):

    def __init__(self, app, workspace):
        super().__init__(app)
        self.workspace = workspace


    @property
    def icon(self):
        return 'rocket_launch'
    
    @property
    def name(self):
        return "Goals"
    
    def render_content(self):
        # with ui.grid(columns='1fr 1fr 1fr 1fr 1fr', rows=('auto', '1fr')).classes('h-full w-full'):
        #     ui.label('This Week')
        #     ui.label('This Month')
        #     ui.label("This Year")
        #     ui.label("This Decade")
        #     ui.label('Before I Die') 

        ui.markdown(
'''
# Priorities
* Adventure & Exploration
* Simplicity
* Companionship & Friendship

# Life Goals
* Marry the girl of my dreams
* Finish my PhD
* Live outside of the city where you can see the stars
* Gain Financial Freedom
* Learn how to play guitar
* Learn a new language


'''
        ).classes('w-full h-full m-4')
    