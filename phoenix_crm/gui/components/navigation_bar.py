"""
Global Navigation Bar Component
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.app import App


class NavigationBar(BoxLayout):
    """Modern navigation bar with back button, title, and user menu."""
    
    def __init__(self, title="Phoenix CRM", show_back=False, on_back=None, on_logout=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(60)
        self.padding = (dp(20), 0)
        self.spacing = dp(15)
        self.on_logout = on_logout
        
        # Background with dark theme color
        with self.canvas.before:
            Color(0.055, 0.055, 0.055, 1)  # #0e0e0e
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        # Logo/Title section
        title_container = BoxLayout(spacing=dp(10))
        
        # Phoenix logo icon
        logo = Label(
            text="🔥",
            font_size='28sp',
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            valign='middle'
        )
        
        # App title - using system default for now
        title_label = Label(
            text=title,
            # font_name='CormorantGaramond',  # Commented out until fonts are installed
            font_size='22sp',
            bold=True,
            color=(1, 1, 1, 1),
            halign='left',
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))
        
        title_container.add_widget(logo)
        title_container.add_widget(title_label)
        self.add_widget(title_container)
        
        # User menu section
        user_menu = BoxLayout(
            size_hint=(None, 1),
            width=dp(100) if on_logout else dp(0),
            spacing=dp(10)
        )
        
        # Logout button - Inter is now default, no need to specify
        if on_logout:
            logout_btn = Button(
                text="Logout",
                size_hint=(None, None),
                size=(dp(90), dp(40)),
                background_color=(0, 0, 0, 0),
                background_normal='',
                color=(1, 1, 1, 1),
                font_size='14sp',
                bold=True
            )
            
            # Add subtle border/background to logout button
            with logout_btn.canvas.before:
                Color(1, 1, 1, 0.15)
                logout_btn._bg = RoundedRectangle(
                    pos=logout_btn.pos,
                    size=logout_btn.size,
                    radius=[dp(6)]
                )
                logout_btn.bind(
                    pos=lambda i, v: setattr(i._bg, 'pos', v),
                    size=lambda i, v: setattr(i._bg, 'size', v)
                )
            
            logout_btn.bind(on_press=lambda x: on_logout())
            user_menu.add_widget(logout_btn)
        
        self.add_widget(user_menu)
    
    def _update_bg(self, instance, value):
        """Update background rectangle position and size."""
        self.bg.pos = self.pos
        self.bg.size = self.size
    
    def update_username(self, username):
        """Update the displayed username."""
        # This method can be used later if you want to show username
        pass
