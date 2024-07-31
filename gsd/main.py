from .app import App

if __name__ in {"__main__", "__mp_main__"}:
    my_app = App()
    my_app.run(devmode=False)