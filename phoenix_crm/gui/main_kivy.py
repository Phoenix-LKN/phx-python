import os
import sys
import threading
import requests

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty
from kivy.graphics import Color, Rectangle, Line, RoundedRectangle  # Add Line import here
from kivymd.app import MDApp
from kivymd.uix.label import MDIcon, MDLabel
from kivymd.uix.card import MDCard

# Handle different KivyMD versions for buttons
try:
    # Try newer KivyMD (2.0+)
    from kivymd.uix.button import MDButton as MDRaisedButton
    from kivymd.uix.button import MDButtonText as MDFlatButton
    from kivymd.uix.button import MDIconButton
    from kivymd.uix.button import MDFloatingActionButton
except ImportError:
    try:
        # Try older KivyMD (1.x)
        from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton, MDFloatingActionButton
    except ImportError:
        # Fallback to basic Kivy buttons if KivyMD buttons not available
        from kivy.uix.button import Button as MDRaisedButton
        from kivy.uix.button import Button as MDFlatButton
        from kivy.uix.button import Button as MDIconButton
        from kivy.uix.button import Button as MDFloatingActionButton

from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.animation import Animation

# Import our leads model - use relative import
try:
    from .leads_model import LeadsModel
except ImportError:
    # Fallback: add parent directory to path
    import sys
    from pathlib import Path
    parent_dir = Path(__file__).parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    from gui.leads_model import LeadsModel

# Import the LeadDrawer component
from gui.components.lead_drawer import LeadDrawer

# --- Kivy App Styling ---
Window.clearcolor = (0.95, 0.96, 0.98, 1)  # Light gray background

class LoginScreen(Screen):
    def __init__(self, on_login_callback, **kwargs):
        super().__init__(**kwargs)
        self.on_login_callback = on_login_callback
        self.backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")

        # Main layout
        layout = BoxLayout(orientation='vertical', padding=40, spacing=15)

        # Title
        title = Label(
            text="Phoenix CRM",
            font_size='32sp',
            bold=True,
            color=(1, 0.4, 0, 1)  # Phoenix Orange
        )
        layout.add_widget(title)

        # Email Input
        self.email_input = TextInput(
            hint_text='Email',
            multiline=False,
            font_size='18sp',
            size_hint_y=None,
            height=50
        )
        layout.add_widget(self.email_input)

        # Password Input
        self.password_input = TextInput(
            hint_text='Password',
            multiline=False,
            password=True,
            font_size='18sp',
            size_hint_y=None,
            height=50
        )
        layout.add_widget(self.password_input)

        # Login Button
        self.login_button = Button(
            text='Login',
            font_size='20sp',
            size_hint_y=None,
            height=55,
            background_color=(1, 0.4, 0, 1),
            background_normal='' # Needed to show color
        )
        self.login_button.bind(on_press=self.login)
        layout.add_widget(self.login_button)

        # Status Label
        self.status_label = Label(text='', color=(1, 0.4, 0.4, 1))
        layout.add_widget(self.status_label)

        self.add_widget(layout)

    def login(self, instance):
        email = self.email_input.text.strip()
        password = self.password_input.text.strip()

        if not email or not password:
            self.status_label.text = "Please enter both email and password"
            return

        self.login_button.disabled = True
        self.login_button.text = "Logging in..."
        self.status_label.text = "Authenticating..."

        # Run network request in a separate thread
        thread = threading.Thread(target=self.auth_thread, args=(email, password), daemon=True)
        thread.start()

    def auth_thread(self, email, password):
        try:
            response = requests.post(
                f"{self.backend_url}/api/auth/login",
                json={"email": email, "password": password},
                timeout=10
            )
            if response.status_code == 200 and response.json().get("access_token"):
                data = response.json()
                token = data["access_token"]
                user = data.get("user", {})  # Extract user object
                Clock.schedule_once(lambda dt: self.login_success(token, user))
            else:
                Clock.schedule_once(lambda dt: self.login_error("Invalid credentials"))
        except requests.exceptions.RequestException:
            Clock.schedule_once(lambda dt: self.login_error("Cannot connect to server"))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.login_error(f"An error occurred: {e}"))

    def login_success(self, token, user):
        self.status_label.text = "Login successful!"
        self.status_label.color = (0.4, 1, 0.4, 1) # Green
        Clock.schedule_once(lambda dt: self.on_login_callback(token, user), 0.5)

    def login_error(self, message):
        self.status_label.text = message
        self.status_label.color = (1, 0.4, 0.4, 1) # Red
        self.login_button.disabled = False
        self.login_button.text = "Login"

class DashboardButton(ButtonBehavior, BoxLayout):
    """ A custom button widget that looks like a card. """
    title = StringProperty('')
    subtitle = StringProperty('')
    icon = StringProperty('')
    screen_name = StringProperty('')  # Add this to identify which screen to navigate to

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_press=self.on_button_press)

    def on_button_press(self, instance):
        print(f"'{self.title}' button pressed")
        app = App.get_running_app()
        
        # Navigate based on screen_name
        if self.screen_name and self.screen_name in app.screen_manager.screen_names:
            app.screen_manager.current = self.screen_name
        else:
            print(f"Screen '{self.screen_name}' not found or not implemented yet")


class LeadsScreen(Screen):
    """Screen to display and manage leads with modern CRM features."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        self.leads_model = None
        self.detail_dialog = None
        self.lead_drawer = None
        
        # Main layout with light background
        main_layout = BoxLayout(orientation='vertical', spacing=0)
        with main_layout.canvas.before:
            Color(0.93, 0.93, 0.93, 1)  # Light gray background
            main_layout.bg_rect = Rectangle(pos=main_layout.pos, size=main_layout.size)
            main_layout.bind(pos=lambda i, v: setattr(main_layout.bg_rect, 'pos', v))
            main_layout.bind(size=lambda i, v: setattr(main_layout.bg_rect, 'size', v))
        
        # Toolbar with search and Add Lead button
        toolbar = BoxLayout(size_hint_y=None, height=dp(90), padding=(dp(25), dp(20)), spacing=dp(15))
        
        # Search field with border
        search_container = BoxLayout(size_hint_y=None, height=dp(50), padding=(dp(15), 0), spacing=dp(10))
        with search_container.canvas.before:
            Color(0.7, 0.7, 0.7, 1)
            border_rect = (
                search_container.x, search_container.y,
                search_container.width, search_container.height
            )
            search_container._border = Line(rectangle=border_rect, width=1.5)
            def update_search_border(instance, value):
                instance._border.rectangle = (
                    instance.x, instance.y,
                    instance.width, instance.height
                )
            search_container.bind(pos=update_search_border, size=update_search_border)

        search_icon = MDIcon(
            icon='magnify',
            theme_text_color="Secondary",
            size_hint_x=None,
            width=dp(30)
        )
        
        self.search_field = TextInput(
            hint_text="Search",
            multiline=False,
            font_size='16sp',
            background_color=(0, 0, 0, 0),
            foreground_color=(0.2, 0.2, 0.2, 1),
            cursor_color=(0, 0, 0, 1),
            padding=(0, dp(15), 0, 0)
        )
        self.search_field.bind(text=self.on_search)
        
        search_container.add_widget(search_icon)
        search_container.add_widget(self.search_field)
        
        # Add Lead button with border
        add_lead_button = Button(
            text="+ Add Lead",
            size_hint=(None, None),
            size=(dp(140), dp(50)),
            background_color=(0, 0, 0, 0),
            background_normal='',
            color=(0.2, 0.2, 0.2, 1),
            font_size='16sp'
        )
        with add_lead_button.canvas.before:
            Color(0.7, 0.7, 0.7, 1)
            border_rect = (
                add_lead_button.x, add_lead_button.y,
                add_lead_button.width, add_lead_button.height
            )
            add_lead_button._border = Line(rectangle=border_rect, width=1.5)
            def update_add_border(instance, value):
                instance._border.rectangle = (
                    instance.x, instance.y,
                    instance.width, instance.height
                )
            add_lead_button.bind(pos=update_add_border, size=update_add_border)

        add_lead_button.bind(on_press=lambda x: print("Add lead clicked"))
        
        toolbar.add_widget(search_container)
        toolbar.add_widget(add_lead_button)
        main_layout.add_widget(toolbar)
        
        # Stats bar
        stats_container = BoxLayout(size_hint_y=None, height=dp(50), padding=(dp(25), 0), spacing=dp(30))
        
        self.total_leads_label = Label(
            text="Total Leads: 0",
            font_size='16sp',
            color=(0, 0, 0, 1),
            bold=True,
            halign='left',
            size_hint_x=None,
            width=dp(150)
        )
        self.total_leads_label.bind(size=self.total_leads_label.setter('text_size'))
        
        self.new_leads_label = Label(
            text="New: 0",
            font_size='16sp',
            color=(0, 0, 0, 1),
            bold=True,
            halign='left',
            size_hint_x=None,
            width=dp(100)
        )
        self.new_leads_label.bind(size=self.new_leads_label.setter('text_size'))

        self.qualified_leads_label = Label(
            text="Qualified: 0",
            font_size='16sp',
            color=(0, 0, 0, 1),
            bold=True,
            halign='left',
            size_hint_x=None,
            width=dp(130)
        )
        self.qualified_leads_label.bind(size=self.qualified_leads_label.setter('text_size'))
        
        stats_container.add_widget(self.total_leads_label)
        stats_container.add_widget(self.new_leads_label)
        stats_container.add_widget(self.qualified_leads_label)
        stats_container.add_widget(Label())  # Spacer
        main_layout.add_widget(stats_container)
        
        # Scrollable leads list
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, bar_width=0)
        
        self.leads_container = BoxLayout(
            orientation='vertical',
            spacing=dp(12),
            padding=(dp(25), dp(10), dp(25), dp(25)),
            size_hint_y=None
        )
        self.leads_container.bind(minimum_height=self.leads_container.setter('height'))
        
        scroll.add_widget(self.leads_container)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
        
        # Initialize lead drawer (hidden initially)
        self.lead_drawer = LeadDrawer(
            backend_url=self.backend_url,
            token=None,  # Will be set when opening
            on_close_callback=self._on_drawer_close,
            on_update_callback=self._on_lead_update
        )
        self.add_widget(self.lead_drawer)
    
    def _on_drawer_close(self):
        """Handle drawer close event."""
        print("Drawer closed")
    
    def _on_lead_update(self, lead_data):
        """Handle lead update from drawer."""
        print(f"Lead updated: {lead_data}")
        # Refresh leads list
        if self.leads_model:
            self.display_leads(self.leads_model.filtered_leads)
    
    def setup_menus(self):
        """Not needed for this design."""
        pass
    
    def on_search(self, instance, value):
        """Handle search input."""
        if self.leads_model:
            filtered = self.leads_model.search_leads(value)
            self.display_leads(filtered)
    
    def filter_leads(self, stage):
        """Filter leads by stage."""
        self.filter_menu.dismiss()
        if self.leads_model:
            self.filter_button.text = f"Filter: {stage.title()}"
            filtered = self.leads_model.filter_by_stage(stage)
            self.display_leads(filtered)
    
    def sort_leads(self, sort_by):
        """Sort leads by specified field."""
        self.sort_menu.dismiss()
        if self.leads_model:
            self.sort_button.text = f"Sort: {sort_by.title()}"
            filtered = self.leads_model.sort_leads(sort_by)
            self.display_leads(filtered)
    
    def on_enter(self):
        """Called when entering this screen."""
        self.load_leads()
    
    def load_leads(self):
        """Fetch leads from the backend."""
        self.leads_container.clear_widgets()
        
        # Show loading indicator
        loading_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=100,
            padding=20
        )
        loading_label = Label(
            text="Loading leads...",
            color=(0.5, 0.5, 0.5, 1),
            font_size='16sp'
        )
        loading_card.add_widget(loading_label)
        self.leads_container.add_widget(loading_card)
        
        # Initialize model
        app = App.get_running_app()
        if not app.user_token:
            self.show_error("Not authenticated")
            return
        
        self.leads_model = LeadsModel(self.backend_url, app.user_token)
        self.leads_model.fetch_leads(self.on_leads_loaded)
    
    def on_leads_loaded(self, success, data):
        """Callback when leads are loaded."""
        if success:
            self.update_stats()
            self.display_leads(data)
        else:
            self.show_error(f"Error: {data}")
    
    def update_stats(self):
        """Update statistics display."""
        if self.leads_model:
            stats = self.leads_model.get_stats()
            self.total_leads_label.text = f"Total Leads: {stats['total']}"
            self.new_leads_label.text = f"New: {stats['new']}"
            self.qualified_leads_label.text = f"Qualified: {stats['qualified']}"
    
    def display_leads(self, leads):
        """Display the leads list with enhanced design."""
        self.leads_container.clear_widgets()
        
        if not leads:
            empty_card = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=200,
                padding=40
            )
            empty_label = Label(
                text="No leads found.\nClick '+ Add Lead' to create your first lead!",
                color=(0.5, 0.5, 0.5, 1),
                font_size='16sp',
                halign='center'
            )
            empty_label.bind(size=empty_label.setter('text_size'))
            empty_card.add_widget(empty_label)
            self.leads_container.add_widget(empty_card)
            return
        
        for lead in leads:
            lead_card = self.create_modern_lead_card(lead)
            self.leads_container.add_widget(lead_card)
    
    def create_modern_lead_card(self, lead):
        """Create a card matching the exact reference design."""
        from kivy.graphics import Color, RoundedRectangle, Line

        class ClickableCard(ButtonBehavior, BoxLayout):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self._border = None
                self._bg = None
                
                with self.canvas.before:
                    Color(0.8, 0.8, 0.8, 1)
                    self._border = Line(width=1.5)
                    Color(1, 1, 1, 1)
                    self._bg = Rectangle()
                
                self.bind(pos=self._update_canvas, size=self._update_canvas)
            
            def _update_canvas(self, instance, value):
                if self._border and self._bg:
                    self._border.rectangle = (
                        self.x, self.y,
                        self.width, self.height
                    )
                    self._bg.pos = self.pos
                    self._bg.size = self.size

        card = ClickableCard(
            size_hint_y=None,
            height=dp(130),
            padding=dp(20),
            spacing=0
        )
        card.bind(on_press=lambda x: self.show_lead_details(lead))
        
        # Left column - contact info
        left_col = BoxLayout(orientation='vertical', spacing=dp(3), size_hint_x=0.65)
        
        # Name
        name = f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip() or "Unnamed Lead"
        name_label = Label(
            text=name,
            font_size='20sp',
            bold=True,
            color=(0, 0, 0, 1),
            halign='left',
            valign='top',
            size_hint_y=None,
            height=dp(30)
        )
        name_label.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
        
        # Company
        company = lead.get('company', 'No Company')
        company_label = Label(
            text=company,
            font_size='14sp',
            color=(0.5, 0.5, 0.5, 1),
            halign='left',
            valign='top',
            size_hint_y=None,
            height=dp(22)
        )
        company_label.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
        
        # Email row
        email_row = BoxLayout(spacing=dp(8), size_hint_y=None, height=dp(24))
        email_icon = MDIcon(
            icon='email-outline',
            theme_text_color="Secondary",
            size_hint_x=None,
            width=dp(20)
        )
        email = lead.get('email', 'No email')
        email_label = Label(
            text=email,
            font_size='14sp',
            color=(0.3, 0.3, 0.3, 1),
            halign='left',
            valign='middle'
        )
        email_label.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
        email_row.add_widget(email_icon)
        email_row.add_widget(email_label)
        
        # Phone row
        phone_row = BoxLayout(spacing=dp(8), size_hint_y=None, height=dp(24))
        phone_icon = MDIcon(
            icon='phone',
            theme_text_color="Secondary",
            size_hint_x=None,
            width=dp(20)
        )
        phone = lead.get('phone', 'No phone')
        phone_label = Label(
            text=phone,
            font_size='14sp',
            color=(0.3, 0.3, 0.3, 1),
            halign='left',
            valign='middle'
        )
        phone_label.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
        phone_row.add_widget(phone_icon)
        phone_row.add_widget(phone_label)
        
        left_col.add_widget(name_label)
        left_col.add_widget(company_label)
        left_col.add_widget(email_row)
        left_col.add_widget(phone_row)
        
        # Right column - status, value, priority
        right_col = BoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint_x=0.35,
            padding=(dp(10), 0, 0, 0)
        )
        
        # Helper function to create badge
        def create_badge(text, width=dp(100)):
            container = BoxLayout(
                size_hint=(None, None),
                size=(width, dp(28)),
                pos_hint={'right': 1}
            )
            
            with container.canvas.before:
                Color(0.92, 0.92, 0.92, 1)
                container._bg = Rectangle()
                
                def update_bg(instance, value):
                    instance._bg.pos = instance.pos
                    instance._bg.size = instance.size
                
                container.bind(pos=update_bg, size=update_bg)
            
            label = Label(
                text=text.upper(),
                font_size='12sp',
                bold=True,
                color=(0.4, 0.4, 0.4, 1)
            )
            container.add_widget(label)
            return container
        
        # Status badge
        status = lead.get('status', 'new')
        status_badge = create_badge(status)
        
        # Value label (centered in remaining space)
        value = lead.get('value', 0)
        value_label = Label(
            text=f"${value:,.2f}",
            font_size='18sp',
            color=(0, 0, 0, 1),
            halign='right',
            valign='middle',
            size_hint_y=1
        )
        value_label.bind(size=value_label.setter('text_size'))
        
        # Priority badge
        priority = lead.get('priority', 'medium')
        priority_text = 'PRIVILIET' if priority == 'high' else priority
        priority_badge = create_badge(priority_text)
        
        right_col.add_widget(status_badge)
        right_col.add_widget(value_label)
        right_col.add_widget(priority_badge)
        
        # Add columns to card
        card.add_widget(left_col)
        card.add_widget(right_col)
        
        return card
    
    def show_lead_details(self, lead):
        """Show detailed lead information in a drawer."""
        # Update drawer token
        app = App.get_running_app()
        self.lead_drawer.token = app.user_token
        
        # Open drawer with lead data
        self.lead_drawer.open(lead)
    
    def show_error(self, message):
        """Display error message."""
        self.leads_container.clear_widgets()
        error_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=120,
            padding=30
        )
        error_label = Label(
            text=message,
            color=(0.9, 0.2, 0.2, 1),
            font_size='16sp',
            halign='center'
        )
        error_label.bind(size=error_label.setter('text_size'))
        
        retry_button = Button(
            text="Retry",
            size_hint=(None, None),
            width=120,
            height=40,
            pos_hint={'center_x': 0.5}
        )
        retry_button.bind(on_press=lambda x: self.load_leads())
        
        error_card.add_widget(error_label)
        error_card.add_widget(retry_button)
        self.leads_container.add_widget(error_card)
    
    def go_back(self, instance):
        """Navigate back to dashboard."""
        app = App.get_running_app()
        app.screen_manager.current = 'dashboard'


class DashboardScreen(Screen):
    def __init__(self, on_logout_callback, **kwargs):
        super().__init__(**kwargs)
        self.on_logout_callback = on_logout_callback
        
        # Main layout
        root_layout = BoxLayout(orientation='vertical', padding=(40, 20, 40, 20), spacing=20)
        
        # Header
        header_layout = BoxLayout(size_hint_y=None, height=50)
        title = Label(
            text="",
            font_size='28sp',
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
            halign='left',
            valign='middle'
        )
        # Keep a reference so we can update it
        self.title_label = title
        title.bind(size=title.setter('text_size'))
        
        logout_button = Button(
            text="Logout",
            size_hint_x=None,
            width=120,
            background_color=(0.9, 0.9, 0.9, 1),
            background_normal='',
            color=(0.2, 0.2, 0.2, 1)
        )
        logout_button.bind(on_press=self.logout)

        header_layout.add_widget(title)
        header_layout.add_widget(logout_button)
        root_layout.add_widget(header_layout)

        # Grid for dashboard buttons
        grid_layout = GridLayout(cols=3, spacing=20)

        # Define dashboard items with Material Design Icon names
        # You can find more icons at: https://pictogrammers.com/library/mdi/
        dashboard_items = [
            {"title": "placeholder", "source": "phx.jpeg"}, # Placeholder for the image
            {"title": "Working Prospects", "subtitle": "Manage your active prospects", "icon": "account-group", "screen": ""},
            {"title": "Follow-Up Tasks", "subtitle": "Track and complete follow-ups", "icon": "calendar-clock", "screen": ""},
            {"title": "Worksheets", "subtitle": "Buyer orders and deal packs", "icon": "file-document-outline", "screen": ""},
            {"title": "My Leads", "subtitle": "View and manage your leads", "icon": "account", "screen": "leads"},
            {"title": "Training Center", "subtitle": "Access training materials", "icon": "school", "screen": ""},
            {"title": "Goals & Accountability", "subtitle": "Track your sales goals", "icon": "flag-checkered", "screen": ""},
            {"title": "Notifications", "subtitle": "View your alerts and updates", "icon": "bell", "screen": ""},
            {"title": "Settings", "subtitle": "Manage your profile and preferences", "icon": "cog", "screen": ""}
        ]

        for item in dashboard_items:
            if item.get("title") == "placeholder":
                # Add the image as a placeholder (using modern properties)
                placeholder_image = Image(
                    source=item.get("source", ""),
                    fit_mode="fill",
                    size_hint=(1, 1)
                )
                grid_layout.add_widget(placeholder_image)
            else:
                button = DashboardButton(
                    title=item["title"],
                    subtitle=item["subtitle"],
                    icon=item["icon"],
                    screen_name=item["screen"]
                )
                grid_layout.add_widget(button)

        root_layout.add_widget(grid_layout)
        self.add_widget(root_layout)

    def on_enter(self):
        """Called when the screen is entered."""
        app = App.get_running_app()
        # Use full_name if available, otherwise email, finally fallback to "User"
        username = getattr(app, 'user_full_name', None) or getattr(app, 'user_email', None) or "User"
        self.title_label.text = f"Welcome, {username}!"

    def logout(self, instance):
        self.on_logout_callback()

class PhoenixCRMApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Orange"
        self.user_token = None
        self.user_full_name = None
        self.user_email = None
        self.screen_manager = ScreenManager()
        
        login_screen = LoginScreen(name='login', on_login_callback=self.on_login_success)
        self.screen_manager.add_widget(login_screen)
        
        dashboard_screen = DashboardScreen(name='dashboard', on_logout_callback=self.on_logout)
        self.screen_manager.add_widget(dashboard_screen)
        
        # Add leads screen
        leads_screen = LeadsScreen(name='leads')
        self.screen_manager.add_widget(leads_screen)

        # For development: bypass login
        self.user_token = "dev_token"  # Set a dummy token
        self.screen_manager.current = 'dashboard'  # Go straight to dashboard
        
        return self.screen_manager

    def on_login_success(self, token, user):
        print(f"Login successful! Token: {token}, User: {user}")
        self.user_token = token
        self.user_full_name = user.get("full_name")
        self.user_email = user.get("email")
        self.screen_manager.current = 'dashboard'

    def on_logout(self):
        self.user_token = None
        self.user_full_name = None
        self.user_email = None
        self.screen_manager.current = 'login'

if __name__ == '__main__':
    try:
        PhoenixCRMApp().run()
    except Exception as e:
        print(f"Error starting Kivy application: {e}")
        sys.exit(1)
