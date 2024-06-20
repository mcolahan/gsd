from dataclasses import dataclass
from gsd.utils.observer import Notifier, ColorListener
from nicegui import ui


@dataclass
class AbstractTheme:
    bg_primary = '#FFFFFF'
    bg_secondary = '#F5F5F5'
    primary = '#61afef'
    secondary = '#ef596f'
    accent = '#d55fde'
    dark = '#000000'
    positive = '#198754'
    negative = '#DC3545'
    info = '#0DCAF0'
    warning = '#FFC107'
    text_class_primary = 'text-slate-100'
    text_class_subtle = 'text-slate-500'
    

class DarkTheme(AbstractTheme):
    bg_primary = '#151515'
    bg_secondary = '#212121'
    text_primary = '#FFFFFF'
    text_class_primary = 'text-zinc-200'
    text_class_subtle = 'text-zinc-500'

class LightTheme(AbstractTheme):
    bg_primary = '#FFFFFF'
    bg_secondary = '#F5F5F5'
    text_primary = '#000000'
    text_class_primary = 'text-slate-900'


class ColorManager(Notifier):

    dark_theme = DarkTheme()
    light_theme = LightTheme()   
    theme = dark_theme
    _instance = None
    _dark_mode = ui.dark_mode()

    def __init__(self):
        super().__init__()


    @classmethod
    def set_mode(cls, mode='dark'):
        if mode == 'dark':
            cls.theme = cls.dark_theme
            if not cls._dark_mode.value:
                cls._dark_mode.toggle()
            
        elif mode == 'light':
            cls.theme = cls.light_theme
            if cls._dark_mode.value:
                cls._dark_mode.toggle()
            # cls._dark_mode.disable()

        for listener in cls.instance().listeners:
            if callable(getattr(listener, 'update_color_theme', None)):
                listener.update_color_theme(cls.theme)

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = ColorManager()
        return cls._instance
    
    @classmethod
    def is_dark_mode(cls):
        return cls.theme is cls.dark_theme



        
    
        

