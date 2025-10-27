"""
Leaderboard Banner Component - Modern stock-ticker style display
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.clock import Clock
import threading
import requests

class LeaderboardBanner(BoxLayout):
    """Stock-ticker style banner displaying top sales performers."""
    
    def __init__(self, backend_url, token, **kwargs):
        super().__init__(**kwargs)
        self.backend_url = backend_url
        self.token = token
        self.leaderboard_data = []
        self.current_period = "monthly"
        
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(140)
        self.spacing = dp(8)
        self.padding = (dp(25), dp(15), dp(25), dp(15))
        
        # Modern dark gradient background
        with self.canvas.before:
            # Dark header strip - even darker
            Color(0.04, 0.04, 0.04, 1)  # Slightly lighter than #0e0e0e
            self._bg_dark = Rectangle(pos=self.pos, size=(self.width, dp(50)))
            # Content area - dark theme
            Color(0.08, 0.08, 0.08, 1)  # Slightly lighter for contrast
            self._bg_light = Rectangle(pos=(self.x, self.y), size=(self.width, self.height - dp(50)))
            # Accent line - orange
            Color(1, 0.4, 0, 1)
            self._accent_line = Rectangle(pos=(self.x, self.y + self.height - dp(3)), size=(self.width, dp(3)))
        
        self.bind(pos=self._update_canvas, size=self._update_canvas)
        
        # Header row
        header = BoxLayout(
            size_hint_y=None, 
            height=dp(50),
            spacing=dp(20), 
            padding=(0, dp(5), 0, dp(5))
        )
        
        # Trophy + Title (left side) with Orbitron font
        title_box = BoxLayout(size_hint_x=None, width=dp(280), spacing=dp(12))
        
        trophy = Label(
            text="🏆",
            font_size='26sp',
            size_hint_x=None,
            width=dp(35)
        )
        
        title = Label(
            text="SALES LEADERBOARD",
            # font_name='CormorantGaramond',  # Commented out until fonts are installed
            font_size='20sp',
            bold=True,
            color=(1, 1, 1, 1),
            halign='left',
            valign='middle'
        )
        title.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
        
        title_box.add_widget(trophy)
        title_box.add_widget(title)
        header.add_widget(title_box)
        
        # Period tabs (center)
        period_tabs = BoxLayout(
            size_hint_x=None, 
            width=dp(360), 
            spacing=dp(8),
            padding=(0, dp(5), 0, dp(5))  # Add vertical padding to tabs
        )
        
        self.all_time_btn = self._create_tab_button("ALL TIME", "all")
        self.monthly_btn = self._create_tab_button("THIS MONTH", "monthly", active=True)
        self.weekly_btn = self._create_tab_button("THIS WEEK", "weekly")
        
        period_tabs.add_widget(self.all_time_btn)
        period_tabs.add_widget(self.monthly_btn)
        period_tabs.add_widget(self.weekly_btn)
        
        header.add_widget(period_tabs)
        header.add_widget(Label())  # Spacer
        
        # Live indicator (right side)
        live_indicator = BoxLayout(size_hint=(None, None), size=(dp(85), dp(32)), spacing=dp(8))
        
        pulse_dot = Label(text="●", font_size='14sp', color=(0.3, 1, 0.3, 1), size_hint_x=None, width=dp(18))
        # Animate the pulse
        anim = Animation(color=(0.3, 1, 0.3, 0.3), duration=0.8) + Animation(color=(0.3, 1, 0.3, 1), duration=0.8)
        anim.repeat = True
        anim.start(pulse_dot)
        
        live_label = Label(text="LIVE", font_size='13sp', bold=True, color=(1, 1, 1, 0.9))
        
        live_indicator.add_widget(pulse_dot)
        live_indicator.add_widget(live_label)
        header.add_widget(live_indicator)
        
        self.add_widget(header)
        
        # Ticker container (scrollable horizontal) with proper spacing
        self.ticker_container = BoxLayout(
            spacing=dp(18),  # Increased spacing between items
            size_hint_y=None,
            height=dp(65),  # Fixed height for ticker items
            padding=(0, 0, 0, 0)
        )
        self.add_widget(self.ticker_container)
        
        # Load initial data
        self.refresh_leaderboard()
    
    def _create_tab_button(self, text, period, active=False):
        """Create a modern tab button - Inter is default."""
        btn = Button(
            text=text,
            # font_name='Inter' - not needed, it's global now
            size_hint_x=1,
            background_color=(0, 0, 0, 0),
            background_normal='',
            color=(1, 1, 1, 1) if active else (1, 1, 1, 0.6),
            font_size='12sp',
            bold=True
        )
        
        with btn.canvas.before:
            if active:
                Color(1, 0.4, 0, 0.95)
            else:
                Color(1, 1, 1, 0.08)  # More subtle when inactive
            btn._bg = RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(6)])
            btn.bind(
                pos=lambda i, v: setattr(i._bg, 'pos', v),
                size=lambda i, v: setattr(i._bg, 'size', v)
            )
        
        btn.bind(on_press=lambda x: self.change_period(period))
        return btn
    
    def change_period(self, period):
        """Change the leaderboard period."""
        self.current_period = period
        
        # Update tab styles
        for btn, p in [(self.all_time_btn, "all"), (self.monthly_btn, "monthly"), (self.weekly_btn, "weekly")]:
            is_active = (p == period)
            btn.bold = is_active
            btn.color = (1, 1, 1, 1) if is_active else (1, 1, 1, 0.6)
            btn.canvas.before.clear()
            with btn.canvas.before:
                Color(1, 0.4, 0, 0.95) if is_active else Color(1, 1, 1, 0.12)
                btn._bg = RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(5)])
                btn.bind(
                    pos=lambda i, v: setattr(i._bg, 'pos', v),
                    size=lambda i, v: setattr(i._bg, 'size', v)
                )
        
        self.refresh_leaderboard()
    
    def refresh_leaderboard(self):
        """Fetch and display leaderboard data."""
        thread = threading.Thread(target=self._fetch_leaderboard, daemon=True)
        thread.start()
    
    def _fetch_leaderboard(self):
        """Background thread for fetching leaderboard."""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.backend_url}/api/leaderboard/?period={self.current_period}&limit=10",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                self.leaderboard_data = response.json()
                Clock.schedule_once(lambda dt: self._update_ui())
            else:
                print(f"Error fetching leaderboard: {response.status_code}")
                
        except Exception as e:
            print(f"Leaderboard fetch error: {e}")
    
    def _update_ui(self):
        """Update the ticker display."""
        self.ticker_container.clear_widgets()
        
        if not self.leaderboard_data:
            no_data = Label(
                text="No sales data available • Close deals to see rankings",
                color=(0.6, 0.6, 0.6, 1),
                font_size='14sp',
                italic=True
            )
            self.ticker_container.add_widget(no_data)
            return
        
        # Show top performers in ticker style - NO SEPARATORS
        for idx, entry in enumerate(self.leaderboard_data[:10], 1):
            item = self._create_ticker_item(entry, idx)
            self.ticker_container.add_widget(item)
    
    def _create_ticker_item(self, entry, position):
        """Create a modern ticker-style item - Inter is default."""
        container = BoxLayout(
            orientation='horizontal',
            spacing=dp(12),
            size_hint=(None, 1),
            width=dp(210),
            padding=(dp(16), dp(8), dp(16), dp(8))
        )
        
        # Darker background for dark theme
        with container.canvas.before:
            Color(0.12, 0.12, 0.12, 1)  # Dark card background
            container._bg = RoundedRectangle(pos=container.pos, size=container.size, radius=[dp(8)])
            container.bind(
                pos=lambda i, v: setattr(i._bg, 'pos', v),
                size=lambda i, v: setattr(i._bg, 'size', v)
            )
        
        # Rank badge
        rank_container = BoxLayout(size_hint_x=None, width=dp(36), padding=(dp(3), dp(3)))
        
        if position <= 3:
            # Medal for top 3
            with rank_container.canvas.before:
                if position == 1:
                    Color(1, 0.84, 0, 1)  # Gold
                elif position == 2:
                    Color(0.75, 0.75, 0.75, 1)  # Silver
                else:
                    Color(0.8, 0.5, 0.2, 1)  # Bronze
                rank_container._bg = RoundedRectangle(radius=[dp(18)])
                rank_container.bind(
                    pos=lambda i, v: setattr(i._bg, 'pos', v),
                    size=lambda i, v: setattr(i._bg, 'size', v)
                )
            
            rank_label = Label(
                text=str(position),
                font_size='16sp',
                bold=True,
                color=(1, 1, 1, 1)
            )
        else:
            # Number for others
            rank_label = Label(
                text=f"#{position}",
                font_size='14sp',
                bold=True,
                color=(0.5, 0.5, 0.5, 1)
            )
        
        rank_container.add_widget(rank_label)
        container.add_widget(rank_container)
        
        # Info column with Inter font
        info_col = BoxLayout(orientation='vertical', spacing=dp(3))
        
        name = entry.get('full_name', 'Unknown')
        if len(name) > 16:
            name = name[:13] + "..."
        
        name_label = Label(
            text=name,
            # font_name='Inter' - not needed anymore
            font_size='14sp',
            bold=True,
            color=(1, 1, 1, 1),
            halign='left',
            valign='top',
            size_hint_y=None,
            height=dp(20)
        )
        
        # Stats row
        if self.current_period == "weekly":
            sales = entry.get('weekly_sales', 0)
            revenue = entry.get('weekly_revenue', 0)
        elif self.current_period == "monthly":
            sales = entry.get('monthly_sales', 0)
            revenue = entry.get('monthly_revenue', 0)
        else:
            sales = entry.get('total_sales', 0)
            revenue = entry.get('total_revenue', 0)
        
        stats_label = Label(
            text=f"{sales} deals • ${revenue/1000:.1f}K" if revenue >= 1000 else f"{sales} deals • ${revenue:.0f}",
            # font_name='Inter' - not needed anymore
            font_size='12sp',
            color=(0.7, 0.7, 0.7, 1),
            halign='left',
            valign='middle',
            size_hint_y=None,
            height=dp(18)
        )
        stats_label.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
        
        info_col.add_widget(name_label)
        info_col.add_widget(stats_label)
        
        container.add_widget(info_col)
        
        return container
    
    def _update_canvas(self, instance, value):
        """Update background graphics."""
        self._bg_dark.pos = (self.x, self.y + self.height - dp(50))  # Updated
        self._bg_dark.size = (self.width, dp(50))  # Updated
        
        self._bg_light.pos = self.pos
        self._bg_light.size = (self.width, self.height - dp(50))  # Updated
        
        self._accent_line.pos = (self.x, self.y + self.height - dp(3))
        self._accent_line.size = (self.width, dp(3))
