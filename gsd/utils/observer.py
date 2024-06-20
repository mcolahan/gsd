from dataclasses import dataclass, field
from abc import ABC

class Listener(ABC):
    def update(self, msg):
        pass

class ColorListener(Listener):
    def update_color_theme(self, theme):
        pass


@dataclass
class Notifier(ABC):
    listeners: list[Listener] = field(default_factory=list)

    def notify_listeners(self, msg):
        for listener in self.listeners:
            listener.update(msg)

    def register_listener(self, listener: Listener):
        self.listeners.append(listener)
    
    def remove_listener(self, listener: Listener):
        if listener in self.listeners:
            self.listeners.remove(listener)


