# highlight_square.py
from kivy.properties import BooleanProperty, ListProperty
from kivy.uix.widget import Widget


class HighlightSquare(Widget):
    highlighted = BooleanProperty(False)
    rgba = ListProperty([0, 0, 0, 0])  # fully transparent default

    def on_highlighted(self, *_):
        self.rgba = [1, 0, 0, 0.35] if self.highlighted else [0, 0, 0, 0]
