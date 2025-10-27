"""
New Modern Dashboard Screen with 3-column grid layout and Supabase integration
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.progressbar import ProgressBar
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.app import App
import os
from datetime import datetime

from gui.components.dashboard_card import DashboardCard
from gui.components.navigation_bar import NavigationBar
from gui.components.leaderboard_banner import LeaderboardBanner


class NewDashboardScreen(Screen):
    """Modern dashboard with 3-column grid layout."""
    
    def __init__(self, on_logout_callback, **kwargs):
        super().__init__(**kwargs)
        self.on_logout_callback = on_logout_callback
        self.backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        
        # Data containers
        self.appointments_data = []
        self.leads_data = []
        self.goals_data = []
        self.notifications_data = []
        self.worksheets_data = []
        self.training_data = []
        
        # Reference to main layout for adding leaderboard later
        self.main_layout = None
        self.leaderboard_banner = None
        self.content_area = None
        
        self._build_ui()
        
        # Don't schedule data refresh on init - wait until screen is entered
        # Clock.schedule_interval will still run for periodic refresh
        Clock.schedule_interval(lambda dt: self.refresh_all_data(), 300)  # Every 5 min
    
    def on_enter(self):
        """Called when the screen is entered (after login)."""
        print("🎯 Dashboard screen entered - triggering data fetch")
        
        # Add leaderboard banner if not already added
        if self.leaderboard_banner is None:
            app = App.get_running_app()
            if app.user_token:
                print("🏆 Adding leaderboard banner to dashboard")
                self.leaderboard_banner = LeaderboardBanner(
                    backend_url=self.backend_url,
                    token=app.user_token
                )
                # Insert leaderboard between nav bar (index 0) and content (index 1)
                self.main_layout.add_widget(self.leaderboard_banner, index=len(self.main_layout.children) - 1)
                print("✅ Leaderboard banner added successfully")
        
        # Fetch data immediately when entering the screen
        self.refresh_all_data()

    def _build_ui(self):
        """Build the dashboard UI."""
        self.main_layout = BoxLayout(orientation='vertical', spacing=0)
        
        # Background
        with self.main_layout.canvas.before:
            Color(0.96, 0.96, 0.96, 1)
            self.main_layout._bg = Rectangle(pos=self.main_layout.pos, size=self.main_layout.size)
        self.main_layout.bind(pos=lambda i, v: setattr(self.main_layout._bg, 'pos', v))
        self.main_layout.bind(size=lambda i, v: setattr(self.main_layout._bg, 'size', v))
        
        # Navigation bar
        nav_bar = NavigationBar(
            title="Phoenix CRM",
            show_back=False,
            on_logout=self.logout
        )
        self.main_layout.add_widget(nav_bar)
        
        # NOTE: Leaderboard banner will be added in on_enter() when user_token is available
        
        # Content area with 3 columns - NO SCROLLVIEW, fixed height
        self.content_area = BoxLayout(
            orientation='horizontal',
            spacing=dp(25),
            padding=(dp(25), dp(25), dp(25), dp(25)),
            size_hint_y=1  # Fill remaining space below navbar
        )
        
        self.content_area.add_widget(self._create_left_column())
        self.content_area.add_widget(self._create_middle_column())
        self.content_area.add_widget(self._create_ai_panel())
        
        self.main_layout.add_widget(self.content_area)
        self.add_widget(self.main_layout)
    
    def _create_left_column(self):
        """Create left column with uniform height."""
        col = BoxLayout(orientation='vertical', spacing=dp(20), size_hint_x=0.3)
        
        # Appointments - takes 1/3 of column height
        self.appointments_card = DashboardCard(title="APPOINTMENTS")
        self.appointments_card.size_hint_y = 0.33
        self.appointments_scroll = ScrollView(size_hint_y=1, do_scroll_x=False, bar_width=0)
        self.appointments_list = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None
        )
        self.appointments_list.bind(minimum_height=self.appointments_list.setter('height'))
        self.appointments_scroll.add_widget(self.appointments_list)
        self.appointments_card.add_widget(self.appointments_scroll)
        col.add_widget(self.appointments_card)
        
        # Leads - takes 1/3 of column height
        self.leads_card = DashboardCard(title="LEADS")
        self.leads_card.size_hint_y = 0.33
        self.leads_scroll = ScrollView(size_hint_y=1, do_scroll_x=False, bar_width=0)
        self.leads_list = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None
        )
        self.leads_list.bind(minimum_height=self.leads_list.setter('height'))
        self.leads_scroll.add_widget(self.leads_list)
        self.leads_card.add_widget(self.leads_scroll)
        col.add_widget(self.leads_card)
        
        # Goals - takes 1/3 of column height
        self.goals_card = DashboardCard(title="GOALS")
        self.goals_card.size_hint_y = 0.34  # Slightly larger to fill remaining space
        
        goals_scroll = ScrollView(size_hint_y=1, do_scroll_x=False, bar_width=0)
        self.goals_content = BoxLayout(
            orientation='vertical',
            spacing=dp(18),
            size_hint_y=None
        )
        self.goals_content.bind(minimum_height=self.goals_content.setter('height'))
        
        goals_scroll.add_widget(self.goals_content)
        self.goals_card.add_widget(goals_scroll)
        col.add_widget(self.goals_card)
        
        return col
    
    def _create_middle_column(self):
        """Create middle column with uniform height."""
        col = BoxLayout(orientation='vertical', spacing=dp(20), size_hint_x=0.3)
        
        # Worksheets - takes ~20% of column height
        self.worksheets_card = DashboardCard(title="WORKSHEETS")
        self.worksheets_card.size_hint_y = 0.4
        worksheets_content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        self.worksheets_list = BoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint_y=None
        )
        self.worksheets_list.bind(minimum_height=self.worksheets_list.setter('height'))
        
        ws_scroll = ScrollView(size_hint_y=1, do_scroll_x=False, bar_width=0)
        ws_scroll.add_widget(self.worksheets_list)
        worksheets_content.add_widget(ws_scroll)
        
        new_ws_btn = Button(
            text="+ New Worksheet",
            size_hint_y=None,
            height=dp(40),
            background_color=(0, 0, 0, 0),
            background_normal='',
            color=(1, 0.4, 0, 1),
            font_size='13sp',
            bold=True
        )
        worksheets_content.add_widget(new_ws_btn)
        self.worksheets_card.add_widget(worksheets_content)
        col.add_widget(self.worksheets_card)
        
        # Notifications - takes ~30% of column height
        self.notifications_card = DashboardCard(title="NOTIFICATIONS")
        self.notifications_card.size_hint_y = 0.3
        self.notifications_scroll = ScrollView(size_hint_y=1, do_scroll_x=False, bar_width=0)
        self.notifications_list = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None
        )
        self.notifications_list.bind(minimum_height=self.notifications_list.setter('height'))
        self.notifications_scroll.add_widget(self.notifications_list)
        self.notifications_card.add_widget(self.notifications_scroll)
        col.add_widget(self.notifications_card)
        
        # Training Center - takes ~50% of column height
        self.training_card = DashboardCard(title="TRAINING CENTER")
        self.training_card.size_hint_y = 0.5
        training_content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        self.training_list = BoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint_y=None
        )
        self.training_list.bind(minimum_height=self.training_list.setter('height'))
        
        training_scroll = ScrollView(size_hint_y=1, do_scroll_x=False, bar_width=0)
        training_scroll.add_widget(self.training_list)
        training_content.add_widget(training_scroll)
        
        open_training_btn = Button(
            text="Open Training Center",
            size_hint_y=None,
            height=dp(40),
            background_color=(0, 0, 0, 0),
            background_normal='',
            color=(1, 0.4, 0, 1),
            font_size='13sp',
            bold=True
        )
        training_content.add_widget(open_training_btn)
        self.training_card.add_widget(training_content)
        col.add_widget(self.training_card)
        
        return col
    
    def _create_ai_panel(self):
        """Create Phoenix AI chat panel with uniform height."""
        ai_panel = DashboardCard(title="Phoenix AI")
        ai_panel.size_hint_x = 0.4
        ai_panel.size_hint_y = 1  # Fill full column height
        
        # Chat history scroll
        chat_scroll = ScrollView(size_hint_y=1, do_scroll_x=False, bar_width=0)
        self.chat_history = BoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint_y=None,
            padding=(0, 0, 0, dp(8))
        )
        self.chat_history.bind(minimum_height=self.chat_history.setter('height'))
        chat_scroll.add_widget(self.chat_history)
        ai_panel.add_widget(chat_scroll)
        
        # Input container at bottom
        input_container = BoxLayout(
            size_hint_y=None,
            height=dp(55),
            spacing=dp(8),
            padding=(0, dp(5), 0, 0)
        )
        
        ai_icon = Label(
            text="🤖",
            font_size='24sp',
            size_hint_x=None,
            width=dp(35)
        )
        
        self.ai_input = TextInput(
            hint_text="Type a message...",
            multiline=False,
            font_size='13sp',
            background_color=(0.95, 0.95, 0.95, 1),
            foreground_color=(0.3, 0.3, 0.3, 1),
            padding=(dp(12), dp(12))
        )
        self.ai_input.bind(on_text_validate=self.send_ai_message)
        
        send_btn = Button(
            text="➤",
            size_hint_x=None,
            width=dp(45),
            background_color=(1, 0.4, 0, 1),
            background_normal='',
            color=(1, 1, 1, 1),
            font_size='18sp',
            bold=True
        )
        send_btn.bind(on_press=self.send_ai_message)
        
        input_container.add_widget(ai_icon)
        input_container.add_widget(self.ai_input)
        input_container.add_widget(send_btn)
        ai_panel.add_widget(input_container)
        
        return ai_panel
    
    def _create_appointment_item(self, client_name, time, status="pending"):
        """Create appointment item with hover effect."""
        
        class HoverableItem(BoxLayout):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.is_hovering = False
                
                with self.canvas.before:
                    # Border
                    Color(0.92, 0.92, 0.92, 1)
                    self._border = RoundedRectangle(
                        pos=self.pos,
                        size=self.size,
                        radius=[dp(8)]
                    )
                    # Background with Color instruction
                    self._bg_color = Color(1, 1, 1, 0)
                    self._bg = RoundedRectangle(
                        pos=self.pos,
                        size=self.size,
                        radius=[dp(8)]
                    )
                
                self.bind(pos=self._update_graphics, size=self._update_graphics)
                Window.bind(mouse_pos=self.on_mouse_pos)
            
            def _update_graphics(self, *args):
                self._border.pos = self.pos
                self._border.size = self.size
                self._bg.pos = self.pos
                self._bg.size = self.size
            
            def on_mouse_pos(self, window, pos):
                if not self.get_root_window():
                    return
                is_colliding = self.collide_point(*self.to_widget(*pos))
                if is_colliding != self.is_hovering:
                    self.is_hovering = is_colliding
                    if is_colliding:
                        # Hover: light background
                        self._bg_color.rgba = (0.98, 0.98, 0.98, 1)
                    else:
                        # Normal: transparent
                        self._bg_color.rgba = (1, 1, 1, 0)
        
        item = HoverableItem(
            size_hint_y=None,
            height=dp(52),
            spacing=dp(10),
            padding=(dp(12), dp(8))
        )
        
        avatar = Label(
            text="👤",
            font_size='22sp',
            size_hint_x=None,
            width=dp(35)
        )
        
        info = BoxLayout(orientation='vertical', spacing=dp(2))
        name_label = Label(
            text=client_name,
            font_size='15sp',
            bold=True,
            color=(0.15, 0.15, 0.15, 1),
            halign='left',
            size_hint_y=None,
            height=dp(20)
        )
        name_label.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
        
        time_label = Label(
            text=time,
            font_size='13sp',
            color=(0.5, 0.5, 0.5, 1),
            halign='left',
            size_hint_y=None,
            height=dp(18)
        )
        time_label.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
        
        info.add_widget(name_label)
        info.add_widget(time_label)
        
        status_colors = {
            'confirmed': (0.2, 0.8, 0.3, 1),
            'pending': (1, 0.6, 0, 1),
            'canceled': (0.9, 0.2, 0.2, 1)
        }
        
        # Modern status indicator
        status_container = BoxLayout(
            orientation='vertical',
            size_hint_x=None,
            width=dp(8),
            padding=(0, dp(10), 0, dp(10))
        )
        status_bar = BoxLayout(size_hint_y=1)
        with status_bar.canvas.before:
            Color(*status_colors.get(status, (0.5, 0.5, 0.5, 1)))
            status_bar._bg = RoundedRectangle(
                pos=status_bar.pos,
                size=status_bar.size,
                radius=[dp(4)]
            )
            status_bar.bind(
                pos=lambda i, v: setattr(i._bg, 'pos', v),
                size=lambda i, v: setattr(i._bg, 'size', v)
            )
        status_container.add_widget(status_bar)
        
        item.add_widget(status_container)
        item.add_widget(avatar)
        item.add_widget(info)
        
        return item
    
    def _create_lead_item(self, name, company, value, stage):
        """Create lead item with hover effect."""
        
        class HoverableLeadItem(BoxLayout):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.is_hovering = False
                
                with self.canvas.before:
                    # Shadow with Color instruction
                    self._shadow_color = Color(0, 0, 0, 0.05)
                    self._shadow = RoundedRectangle(
                        pos=(self.x, self.y - dp(2)),
                        size=self.size,
                        radius=[dp(8)]
                    )
                    # Border
                    Color(0.9, 0.9, 0.9, 1)
                    self._border = RoundedRectangle(
                        pos=self.pos,
                        size=self.size,
                        radius=[dp(8)]
                    )
                    # Background
                    Color(1, 1, 1, 1)
                    self._bg = RoundedRectangle(
                        pos=self.pos,
                        size=self.size,
                        radius=[dp(8)]
                    )
                
                self.bind(pos=self._update_graphics, size=self._update_graphics)
                Window.bind(mouse_pos=self.on_mouse_pos)
            
            def _update_graphics(self, *args):
                self._bg.pos = self.pos
                self._bg.size = self.size
                self._border.pos = self.pos
                self._border.size = self.size
                self._shadow.pos = (self.x, self.y - dp(2))
                self._shadow.size = self.size
            
            def on_mouse_pos(self, window, pos):
                if not self.get_root_window():
                    return
                is_colliding = self.collide_point(*self.to_widget(*pos))
                if is_colliding != self.is_hovering:
                    self.is_hovering = is_colliding
                    if is_colliding:
                        # Hover: elevate shadow
                        self._shadow.pos = (self.x, self.y - dp(4))
                        self._shadow_color.rgba = (0, 0, 0, 0.12)
                    else:
                        # Normal
                        self._shadow.pos = (self.x, self.y - dp(2))
                        self._shadow_color.rgba = (0, 0, 0, 0.05)
        
        item = HoverableLeadItem(
            size_hint_y=None,
            height=dp(56),
            spacing=dp(10),
            padding=(dp(16), dp(10))
        )
        
        avatar = Label(text="👤", font_size='24sp', size_hint_x=None, width=dp(40))
        
        info = BoxLayout(orientation='vertical', spacing=dp(3))
        name_label = Label(
            text=name,
            font_size='15sp',
            bold=True,
            color=(0.15, 0.15, 0.15, 1),
            halign='left',
            size_hint_y=None,
            height=dp(20)
        )
        name_label.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
        
        company_label = Label(
            text=company,
            font_size='13sp',
            color=(0.5, 0.5, 0.5, 1),
            halign='left',
            size_hint_y=None,
            height=dp(18)
        )
        company_label.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
        
        info.add_widget(name_label)
        info.add_widget(company_label)
        item.add_widget(avatar)
        item.add_widget(info)
        return item
    
    def _create_goal_item(self, title, progress=0):
        """Create goal item with proper spacing for progress bar."""
        container = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80), spacing=dp(12))
        
        # Title row with icon
        title_row = BoxLayout(size_hint_y=None, height=dp(32), spacing=dp(8))
        
        target_icon = Label(
            text="🎯",
            font_size='18sp',
            size_hint_x=None,
            width=dp(28)
        )
        
        title_label = Label(
            text=title,
            font_size='14sp',
            bold=True,
            color=(0.25, 0.25, 0.25, 1),
            halign='left',
            valign='middle'
        )
        title_label.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
        
        progress_text = Label(
            text=f"{int(progress)}%",
            font_size='14sp',
            bold=True,
            color=(1, 0.4, 0, 1),
            size_hint_x=None,
            width=dp(50),
            halign='right'
        )
        
        title_row.add_widget(target_icon)
        title_row.add_widget(title_label)
        title_row.add_widget(progress_text)
        
        # Progress bar with custom styling
        progress_container = BoxLayout(size_hint_y=None, height=dp(14))
        
        with progress_container.canvas.before:
            # Background track
            Color(0.9, 0.9, 0.9, 1)
            progress_container._track = RoundedRectangle(
                pos=progress_container.pos,
                size=progress_container.size,
                radius=[dp(7)]
            )
            # Progress fill
            Color(1, 0.4, 0, 1)
            progress_container._fill = RoundedRectangle(
                pos=progress_container.pos,
                size=(progress_container.width * (progress / 100), progress_container.height),
                radius=[dp(7)]
            )
        
        def update_progress_bar(instance, value):
            instance._track.pos = instance.pos
            instance._track.size = instance.size
            instance._fill.pos = instance.pos
            instance._fill.size = (instance.width * (progress / 100), instance.height)
        
        progress_container.bind(pos=update_progress_bar, size=update_progress_bar)
        
        container.add_widget(title_row)
        container.add_widget(progress_container)
        return container
    
    def _create_list_item(self, text, icon=""):
        """Create generic list item with modern styling and better icons."""
        
        class HoverableListItem(BoxLayout):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.is_hovering = False
                
                with self.canvas.before:
                    self._bg_color = Color(0.98, 0.98, 0.98, 0)
                    self._bg = RoundedRectangle(
                        pos=self.pos,
                        size=self.size,
                        radius=[dp(8)]
                    )
                    # Add subtle left border accent
                    self._accent_color = Color(1, 0.4, 0, 0)
                    self._accent = RoundedRectangle(
                        pos=self.pos,
                        size=(dp(3), self.height),
                        radius=[dp(2), 0, 0, dp(2)]
                    )
                
                self.bind(pos=self._update_bg, size=self._update_bg)
                Window.bind(mouse_pos=self.on_mouse_pos)
            
            def _update_bg(self, *args):
                self._bg.pos = self.pos
                self._bg.size = self.size
                self._accent.pos = self.pos
                self._accent.size = (dp(3), self.height)
            
            def on_mouse_pos(self, window, pos):
                if not self.get_root_window():
                    return
                is_colliding = self.collide_point(*self.to_widget(*pos))
                if is_colliding != self.is_hovering:
                    self.is_hovering = is_colliding
                    if is_colliding:
                        self._bg_color.rgba = (0.96, 0.96, 0.96, 1)
                        self._accent_color.rgba = (1, 0.4, 0, 1)
                    else:
                        self._bg_color.rgba = (0.98, 0.98, 0.98, 0)
                        self._accent_color.rgba = (1, 0.4, 0, 0)
        
        item = HoverableListItem(
            size_hint_y=None,
            height=dp(42),
            padding=(dp(12), dp(6)),
            spacing=dp(10)
        )
        
        # Icon with background circle
        if icon:
            icon_container = BoxLayout(
                size_hint_x=None,
                width=dp(32),
                padding=(dp(4), dp(4))
            )
            
            with icon_container.canvas.before:
                Color(0.95, 0.95, 0.95, 1)
                icon_container._bg = RoundedRectangle(
                    pos=icon_container.pos,
                    size=icon_container.size,
                    radius=[dp(16)]
                )
                icon_container.bind(
                    pos=lambda i, v: setattr(i._bg, 'pos', v),
                    size=lambda i, v: setattr(i._bg, 'size', v)
                )
            
            icon_label = Label(
                text=icon,
                font_size='18sp',
                halign='center',
                valign='middle'
            )
            icon_container.add_widget(icon_label)
            item.add_widget(icon_container)
        
        # Text content
        text_container = BoxLayout(orientation='vertical', spacing=dp(2))
        
        main_label = Label(
            text=text,
            font_size='13sp',
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            halign='left',
            valign='middle',
            size_hint_y=None,
            height=dp(18)
        )
        main_label.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
        
        # ADD THE LABEL TO THE CONTAINER - THIS WAS MISSING!
        text_container.add_widget(main_label)
        item.add_widget(text_container)
        
        # Chevron indicator
        chevron = Label(
            text="›",
            font_size='20sp',
            color=(0.6, 0.6, 0.6, 1),
            size_hint_x=None,
            width=dp(20)
        )
        item.add_widget(chevron)
        
        return item

    def refresh_all_data(self):
        """Refresh all dashboard data from backend."""
        import threading
        thread = threading.Thread(target=self._fetch_all_data, daemon=True)
        thread.start()
    
    def _fetch_all_data(self):
        """Fetch data from backend in background thread."""
        import requests
        
        app = App.get_running_app()
        if not app.user_token:
            print("⚠️ No user token available for data fetch")
            return
        
        headers = {"Authorization": f"Bearer {app.user_token}"}
        print(f"🔄 Fetching dashboard data with token: {app.user_token[:20]}...")
        
        try:
            # Fetch appointments
            print("📅 Fetching appointments...")
            resp = requests.get(f"{self.backend_url}/api/appointments/", headers=headers, timeout=5)
            print(f"  Status: {resp.status_code}")
            if resp.status_code == 200:
                self.appointments_data = resp.json()[:5]
                print(f"  ✓ Got {len(self.appointments_data)} appointments")
                Clock.schedule_once(lambda dt: self._update_appointments())
            else:
                print(f"  ✗ Error: {resp.text}")
        except Exception as e:
            print(f"  ✗ Exception: {e}")
        
        try:
            # Fetch leads
            print("👤 Fetching leads...")
            resp = requests.get(f"{self.backend_url}/api/leads/", headers=headers, timeout=5)
            print(f"  Status: {resp.status_code}")
            if resp.status_code == 200:
                self.leads_data = resp.json()[:5]
                print(f"  ✓ Got {len(self.leads_data)} leads")
                Clock.schedule_once(lambda dt: self._update_leads())
            else:
                print(f"  ✗ Error: {resp.text}")
        except Exception as e:
            print(f"  ✗ Exception: {e}")
        
        try:
            # Fetch goals
            print("🎯 Fetching goals...")
            resp = requests.get(f"{self.backend_url}/api/goals/", headers=headers, timeout=5)
            print(f"  Status: {resp.status_code}")
            if resp.status_code == 200:
                self.goals_data = resp.json()[:3]
                print(f"  ✓ Got {len(self.goals_data)} goals")
                Clock.schedule_once(lambda dt: self._update_goals())
            else:
                print(f"  ✗ Error: {resp.text}")
        except Exception as e:
            print(f"  ✗ Exception: {e}")
        
        try:
            # Fetch notifications
            print("🔔 Fetching notifications...")
            resp = requests.get(f"{self.backend_url}/api/notifications/", headers=headers, timeout=5)
            print(f"  Status: {resp.status_code}")
            if resp.status_code == 200:
                self.notifications_data = resp.json()[:5]
                print(f"  ✓ Got {len(self.notifications_data)} notifications")
                Clock.schedule_once(lambda dt: self._update_notifications())
            else:
                print(f"  ✗ Error: {resp.text}")
        except Exception as e:
            print(f"  ✗ Exception: {e}")
        
        try:
            # Fetch worksheets
            print("📄 Fetching worksheets...")
            resp = requests.get(f"{self.backend_url}/api/worksheets/", headers=headers, timeout=5)
            print(f"  Status: {resp.status_code}")
            if resp.status_code == 200:
                self.worksheets_data = resp.json()[:3]
                print(f"  ✓ Got {len(self.worksheets_data)} worksheets")
                Clock.schedule_once(lambda dt: self._update_worksheets())
            else:
                print(f"  ✗ Error: {resp.text}")
        except Exception as e:
            print(f"  ✗ Exception: {e}")
        
        try:
            # Fetch training
            print("📚 Fetching training...")
            resp = requests.get(f"{self.backend_url}/api/training/", headers=headers, timeout=5)
            print(f"  Status: {resp.status_code}")
            if resp.status_code == 200:
                self.training_data = resp.json()[:5]
                print(f"  ✓ Got {len(self.training_data)} training items")
                Clock.schedule_once(lambda dt: self._update_training())
            else:
                print(f"  ✗ Error: {resp.text}")
        except Exception as e:
            print(f"  ✗ Exception: {e}")
        
        print("✅ Dashboard data fetch complete")
    
    def _update_appointments(self):
        """Update appointments UI."""
        print(f"📊 Updating appointments UI with {len(self.appointments_data)} items")
        self.appointments_list.clear_widgets()
        
        if not self.appointments_data:
            print("  ⚠️ No appointments data to display")
            return
        
        for appt in self.appointments_data:
            try:
                # Parse datetime more safely
                time_str = appt.get('appointment_time', '')
                if time_str:
                    time_dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                    time_formatted = time_dt.strftime('%I:%M %p')
                else:
                    time_formatted = "No time"
                
                item = self._create_appointment_item(
                    appt.get('client_name', 'Unknown'),
                    time_formatted,
                    appt.get('status', 'pending')
                )
                self.appointments_list.add_widget(item)
                print(f"  ✓ Added appointment: {appt.get('client_name')} at {time_formatted}")
            except Exception as e:
                print(f"  ✗ Error creating appointment item: {e}")
                print(f"    Appointment data: {appt}")
        
        print(f"  ✅ Appointments UI updated with {len(self.appointments_list.children)} widgets")
    
    def _update_leads(self):
        """Update leads UI."""
        print(f"📊 Updating leads UI with {len(self.leads_data)} items")
        self.leads_list.clear_widgets()
        
        if not self.leads_data:
            print("  ⚠️ No leads data to display")
            return
        
        for lead in self.leads_data:
            try:
                name = f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip()
                if not name:
                    name = "Unnamed Lead"
                
                item = self._create_lead_item(
                    name,
                    lead.get('company', 'No Company'),
                    lead.get('value', 0),
                    lead.get('status', 'new')
                )
                self.leads_list.add_widget(item)
                print(f"  ✓ Added lead: {name}")
            except Exception as e:
                print(f"  ✗ Error creating lead item: {e}")
                print(f"    Lead data: {lead}")
        
        print(f"  ✅ Leads UI updated with {len(self.leads_list.children)} widgets")
    
    def _update_goals(self):
        """Update goals UI."""
        print(f"📊 Updating goals UI with {len(self.goals_data)} items")
        self.goals_content.clear_widgets()
        
        if not self.goals_data:
            print("  ⚠️ No goals data to display")
            return
        
        for goal in self.goals_data:
            try:
                progress = float(goal.get('progress', 0))
                item = self._create_goal_item(goal.get('title', 'Untitled Goal'), progress)
                self.goals_content.add_widget(item)
                print(f"  ✓ Added goal: {goal.get('title')} ({progress}%)")
            except Exception as e:
                print(f"  ✗ Error creating goal item: {e}")
                print(f"    Goal data: {goal}")
        
        print(f"  ✅ Goals UI updated with {len(self.goals_content.children)} widgets")
    
    def _update_worksheets(self):
        """Update worksheets UI."""
        print(f"📊 Updating worksheets UI with {len(self.worksheets_data)} items")
        self.worksheets_list.clear_widgets()
        
        if not self.worksheets_data:
            print("  ⚠️ No worksheets data to display")
            # Add a placeholder
            placeholder = self._create_list_item("No worksheets yet", "📄")
            self.worksheets_list.add_widget(placeholder)
            return
        
        for ws in self.worksheets_data:
            try:
                item = self._create_list_item(ws.get('title', 'Untitled'), "📄")
                self.worksheets_list.add_widget(item)
                print(f"  ✓ Added worksheet: {ws.get('title')}")
            except Exception as e:
                print(f"  ✗ Error creating worksheet item: {e}")
        
        print(f"  ✅ Worksheets UI updated")
    
    def _update_notifications(self):
        """Update notifications UI with enhanced visuals and proper icons."""
        print(f"📊 Updating notifications UI with {len(self.notifications_data)} items")
        self.notifications_list.clear_widgets()
        
        if not self.notifications_data:
            print("  ⚠️ No notifications data to display")
            return
        
        # Map notification types to simple ASCII icons that will render
        notification_icons = {
            'lead': '*',
            'appointment': '>',
            'reminder': '!',
            'goal': '+',
            'update': '#',
            'system': '@',
            'message': 'M',
            'alert': '!',
            'success': 'V',
            'task': '-'
        }
        
        for notif in self.notifications_data:
            try:
                notif_type = str(notif.get('type', 'system')).lower()
                icon = notification_icons.get(notif_type, '*')
                
                # Create enhanced notification item
                item = self._create_notification_item(
                    notif.get('title', 'No title'),
                    notif.get('message', ''),
                    icon,
                    notif.get('read', False)
                )
                self.notifications_list.add_widget(item)
                print(f"  ✓ Added notification: {notif.get('title')} with icon {icon}")
            except Exception as e:
                print(f"  ✗ Error creating notification item: {e}")
        
        print(f"  ✅ Notifications UI updated")
    
    def _create_notification_item(self, title, message, icon, is_read):
        """Create enhanced notification item with icon and read status."""
        
        class HoverableNotification(BoxLayout):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.is_hovering = False
                
                with self.canvas.before:
                    self._bg_color = Color(0.98, 0.98, 0.98, 0)
                    self._bg = RoundedRectangle(
                        pos=self.pos,
                        size=self.size,
                        radius=[dp(8)]
                    )
                
                self.bind(pos=self._update_bg, size=self._update_bg)
                Window.bind(mouse_pos=self.on_mouse_pos)
            
            def _update_bg(self, *args):
                self._bg.pos = self.pos
                self._bg.size = self.size
            
            def on_mouse_pos(self, window, pos):
                if not self.get_root_window():
                    return
                is_colliding = self.collide_point(*self.to_widget(*pos))
                if is_colliding != self.is_hovering:
                    self.is_hovering = is_colliding
                    self._bg_color.rgba = (0.95, 0.95, 0.95, 1) if is_colliding else (0.98, 0.98, 0.98, 0)
        
        item = HoverableNotification(
            size_hint_y=None,
            height=dp(65),
            padding=(dp(12), dp(8)),
            spacing=dp(10)
        )
        
        # Icon with colored background
        icon_container = BoxLayout(
            size_hint_x=None,
            width=dp(40),
            padding=(dp(4), dp(4))
        )
        
        bg_color = (0.95, 0.95, 0.95, 1) if is_read else (1, 0.95, 0.9, 1)
        
        with icon_container.canvas.before:
            Color(*bg_color)
            icon_container._bg = RoundedRectangle(
                pos=icon_container.pos,
                size=icon_container.size,
                radius=[dp(20)]
            )
            icon_container.bind(
                pos=lambda i, v: setattr(i._bg, 'pos', v),
                size=lambda i, v: setattr(i._bg, 'size', v)
            )
        
        icon_label = Label(
            text=icon,
            font_size='22sp',
            halign='center',
            valign='middle'
        )
        icon_container.add_widget(icon_label)
        item.add_widget(icon_container)
        
        # Text content
        text_container = BoxLayout(orientation='vertical', spacing=dp(3))
        
        title_label = Label(
            text=title,
            font_size='14sp',
            bold=not is_read,
            color=(0.2, 0.2, 0.2, 1) if not is_read else (0.5, 0.5, 0.5, 1),
            halign='left',
            valign='top',
            size_hint_y=None,
            height=dp(20)
        )
        title_label.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
        
        message_label = Label(
            text=message[:60] + "..." if len(message) > 60 else message,
            font_size='12sp',
            color=(0.5, 0.5, 0.5, 1),
            halign='left',
            valign='top',
            size_hint_y=None,
            height=dp(30)
        )
        message_label.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
        
        text_container.add_widget(title_label)
        text_container.add_widget(message_label)
        item.add_widget(text_container)
        
        # Unread indicator
        if not is_read:
            unread_dot = Label(
                text="●",
                font_size='12sp',
                color=(1, 0.4, 0, 1),
                size_hint_x=None,
                width=dp(20)
            )
            item.add_widget(unread_dot)
        
        return item
    
    def _update_training(self):
        """Update training UI with enhanced visuals and category-specific icons."""
        print(f"📊 Updating training UI with {len(self.training_data)} items")
        self.training_list.clear_widgets()
        
        if not self.training_data:
            print("  ⚠️ No training data to display")
            return
        
        # Map categories to simple ASCII icons that will render
        category_icons = {
            'software training': 'PC',
            'sales skills': '$',
            'sales': '$',
            'client relations': '<>',
            'market knowledge': '^',
            'market': '^',
            'marketing': '#',
            'productivity': '++',
            'legal': 'L',
            'compliance': 'C',
            'personal development': '+',
            'development': 'D',
            'communication': 'M',
            'negotiation': '<>',
            'leadership': 'L',
            'technology': 'T',
            'finance': '$',
            'strategy': 'S',
            'customer service': '*',
            'customer': '*',
            'presentation': 'P',
            'training': 'T'
        }
        
        for training in self.training_data:
            try:
                category_raw = training.get('category', '')
                category = str(category_raw).lower() if category_raw else ''
                
                # Try exact match first
                icon = category_icons.get(category)
                
                # If no exact match, try partial match
                if not icon and category:
                    for key, value in category_icons.items():
                        if key in category or category in key:
                            icon = value
                            break
                
                # Default icon if no match
                if not icon:
                    icon = 'T'
                
                created_str = training.get('created_at', '')
                if created_str:
                    created_dt = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                    created_formatted = created_dt.strftime('%b %d')
                else:
                    created_formatted = ""
                
                title = training.get('title', 'Untitled')
                display_category = training.get('category', 'Training')
                
                # Create enhanced training item
                item = self._create_training_item(title, display_category, icon, created_formatted)
                self.training_list.add_widget(item)
                print(f"  ✓ Added training: {title} with icon {icon}")
            except Exception as e:
                print(f"  ✗ Error creating training item: {e}")
        
        print(f"  ✅ Training UI updated")
    
    def _create_training_item(self, title, category, icon, date):
        """Create enhanced training item with icon and category."""
        
        class HoverableTraining(BoxLayout):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.is_hovering = False
                
                with self.canvas.before:
                    self._bg_color = Color(0.98, 0.98, 0.98, 0)
                    self._bg = RoundedRectangle(
                        pos=self.pos,
                        size=self.size,
                        radius=[dp(8)]
                    )
                
                self.bind(pos=self._update_bg, size=self._update_bg)
                Window.bind(mouse_pos=self.on_mouse_pos)
            
            def _update_bg(self, *args):
                self._bg.pos = self.pos
                self._bg.size = self.size
            
            def on_mouse_pos(self, window, pos):
                if not self.get_root_window():
                    return
                is_colliding = self.collide_point(*self.to_widget(*pos))
                if is_colliding != self.is_hovering:
                    self.is_hovering = is_colliding
                    self._bg_color.rgba = (0.95, 0.95, 0.95, 1) if is_colliding else (0.98, 0.98, 0.98, 0)
        
        item = HoverableTraining(
            size_hint_y=None,
            height=dp(60),
            padding=(dp(12), dp(8)),
            spacing=dp(10)
        )
        
        # Icon with gradient-like background
        icon_container = BoxLayout(
            size_hint_x=None,
            width=dp(40),
            padding=(dp(4), dp(4))
        )
        
        with icon_container.canvas.before:
            Color(1, 0.95, 0.9, 1)
            icon_container._bg = RoundedRectangle(
                pos=icon_container.pos,
                size=icon_container.size,
                radius=[dp(20)]
            )
            icon_container.bind(
                pos=lambda i, v: setattr(i._bg, 'pos', v),
                size=lambda i, v: setattr(i._bg, 'size', v)
            )
        
        icon_label = Label(
            text=icon,
            font_size='24sp',  # Increased font size
            bold=True,
            color=(1, 0.4, 0, 1),  # Orange color for visibility
            halign='center',
            valign='middle'
        )
        icon_container.add_widget(icon_label)
        item.add_widget(icon_container)
        
        # Text content
        text_container = BoxLayout(orientation='vertical', spacing=dp(2))
        
        title_label = Label(
            text=title,
            font_size='13sp',
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            halign='left',
            valign='top',
            size_hint_y=None,
            height=dp(20)
        )
        title_label.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
        
        # Category and date row
        meta_row = BoxLayout(size_hint_y=None, height=dp(18), spacing=dp(8))
        
        category_label = Label(
            text=category if category else "Training",
            font_size='11sp',
            color=(0.6, 0.6, 0.6, 1),
            halign='left',
            valign='middle'
        )
        category_label.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
        
        if date:
            date_label = Label(
                text=f"• {date}",
                font_size='11sp',
                color=(0.6, 0.6, 0.6, 1),
                size_hint_x=None,
                width=dp(60),
                halign='right'
            )
            meta_row.add_widget(category_label)
            meta_row.add_widget(date_label)
        else:
            meta_row.add_widget(category_label)
        
        text_container.add_widget(title_label)
        text_container.add_widget(meta_row)
        item.add_widget(text_container)
        
        # Play icon
        play_icon = Label(
            text="▶",
            font_size='18sp',  # Increased font size
            bold=True,
            color=(1, 0.4, 0, 1),
            size_hint_x=None,
            width=dp(24)
        )
        item.add_widget(play_icon)
        
        return item

    def send_ai_message(self, instance):
        """Send AI message."""
        message = self.ai_input.text.strip()
        if not message:
            return
        self.ai_input.text = ""
        # TODO: Implement AI backend call
    
    def logout(self):
        """Handle logout."""
        self.on_logout_callback()
