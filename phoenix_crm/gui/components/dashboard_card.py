"""
Reusable Dashboard Card Component with modern styling
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
from kivy.animation import Animation


class DashboardCard(BoxLayout):
    """A modern card widget with shadow and hover effects."""
    
    def __init__(self, title="", **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(20)
        self.spacing = dp(12)
        self.size_hint_y = None
        
        # Card background with multi-layer shadow for depth
        with self.canvas.before:
            # Outer shadow (blur effect simulation)
            Color(0, 0, 0, 0.03)
            self._shadow3 = RoundedRectangle(
                pos=(self.x - dp(3), self.y - dp(5)),
                size=(self.width + dp(6), self.height + dp(6)),
                radius=[dp(14)]
            )
            # Middle shadow
            Color(0, 0, 0, 0.06)
            self._shadow2 = RoundedRectangle(
                pos=(self.x - dp(2), self.y - dp(3)),
                size=(self.width + dp(4), self.height + dp(4)),
                radius=[dp(13)]
            )
            # Inner shadow
            Color(0, 0, 0, 0.08)
            self._shadow1 = RoundedRectangle(
                pos=(self.x - dp(1), self.y - dp(2)),
                size=(self.width + dp(2), self.height + dp(2)),
                radius=[dp(12)]
            )
            # Card background
            Color(1, 1, 1, 1)
            self._bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )
            # Subtle border
            Color(0.94, 0.94, 0.94, 1)
            self._border = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )
        
        self.bind(pos=self._update_canvas, size=self._update_canvas)
        
        # Card title
        if title:
            title_label = Label(
                text=title,
                font_size='15sp',
                bold=True,
                color=(0.2, 0.2, 0.2, 1),
                size_hint_y=None,
                height=dp(22),
                halign='left',
                valign='middle'
            )
            title_label.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
            self.add_widget(title_label)
    
    def _update_canvas(self, instance, value):
        """Update card graphics with proper layering."""
        # Update background
        self._bg.pos = self.pos
        self._bg.size = self.size
        
        # Update border (slightly inset)
        self._border.pos = (self.x + 0.5, self.y + 0.5)
        self._border.size = (self.width - 1, self.height - 1)
        
        # Update shadows with offset
        self._shadow1.pos = (self.x, self.y - dp(2))
        self._shadow1.size = (self.width, self.height + dp(2))
        
        self._shadow2.pos = (self.x - dp(1), self.y - dp(3))
        self._shadow2.size = (self.width + dp(2), self.height + dp(4))
        
        self._shadow3.pos = (self.x - dp(2), self.y - dp(5))
        self._shadow3.size = (self.width + dp(4), self.height + dp(6))
