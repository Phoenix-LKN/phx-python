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
from kivymd.app import MDApp
from kivymd.uix.label import MDIcon
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView

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
                token = response.json()["access_token"]
                Clock.schedule_once(lambda dt: self.login_success(token))
            else:
                Clock.schedule_once(lambda dt: self.login_error("Invalid credentials"))
        except requests.exceptions.RequestException:
            Clock.schedule_once(lambda dt: self.login_error("Cannot connect to server"))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.login_error(f"An error occurred: {e}"))

    def login_success(self, token):
        self.status_label.text = "Login successful!"
        self.status_label.color = (0.4, 1, 0.4, 1) # Green
        Clock.schedule_once(lambda dt: self.on_login_callback(token), 0.5)

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
    """Screen to display and manage leads."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', spacing=0)
        
        # Header with gradient background
        header = BoxLayout(size_hint_y=None, height=70, padding=(20, 10))
        with header.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(1, 0.4, 0, 1)  # Orange background
            header.rect = Rectangle(pos=header.pos, size=header.size)
            header.bind(pos=lambda instance, value: setattr(header.rect, 'pos', value))
            header.bind(size=lambda instance, value: setattr(header.rect, 'size', value))
        
        back_button = Button(
            text="← Back",
            size_hint=(None, None),
            width=100,
            height=40,
            background_color=(1, 1, 1, 0.2),
            background_normal='',
            color=(1, 1, 1, 1),
            bold=True
        )
        back_button.bind(on_press=self.go_back)
        
        title = Label(
            text="My Leads",
            font_size='26sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_x=1
        )
        
        # Add lead button
        add_button = Button(
            text="+ Add Lead",
            size_hint=(None, None),
            width=140,
            height=40,
            background_color=(1, 1, 1, 1),
            background_normal='',
            color=(1, 0.4, 0, 1),
            bold=True
        )
        add_button.bind(on_press=lambda x: print("Add lead clicked"))
        
        header.add_widget(back_button)
        header.add_widget(title)
        header.add_widget(add_button)
        main_layout.add_widget(header)
        
        # Stats bar
        stats_container = BoxLayout(size_hint_y=None, height=80, padding=20, spacing=10)
        stats_container.canvas.before.clear()
        with stats_container.canvas.before:
            Color(0.97, 0.97, 0.97, 1)
            stats_container.rect = Rectangle(pos=stats_container.pos, size=stats_container.size)
            stats_container.bind(pos=lambda instance, value: setattr(stats_container.rect, 'pos', value))
            stats_container.bind(size=lambda instance, value: setattr(stats_container.rect, 'size', value))
        
        self.total_leads_label = Label(
            text="Total: 0",
            font_size='14sp',
            color=(0.3, 0.3, 0.3, 1),
            bold=True
        )
        self.new_leads_label = Label(
            text="New: 0",
            font_size='14sp',
            color=(0.2, 0.7, 0.3, 1),
            bold=True
        )
        self.qualified_leads_label = Label(
            text="Qualified: 0",
            font_size='14sp',
            color=(0.2, 0.5, 0.9, 1),
            bold=True
        )
        
        stats_container.add_widget(self.total_leads_label)
        stats_container.add_widget(self.new_leads_label)
        stats_container.add_widget(self.qualified_leads_label)
        main_layout.add_widget(stats_container)
        
        # Scrollable leads list
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        
        self.leads_container = BoxLayout(
            orientation='vertical',
            spacing=15,
            padding=(20, 15),
            size_hint_y=None
        )
        self.leads_container.bind(minimum_height=self.leads_container.setter('height'))
        
        scroll.add_widget(self.leads_container)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
    
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
        
        thread = threading.Thread(target=self.fetch_leads_thread, daemon=True)
        thread.start()
    
    def fetch_leads_thread(self):
        """Fetch leads in background thread."""
        try:
            app = App.get_running_app()
            if not app.user_token:
                Clock.schedule_once(lambda dt: self.show_error("Not authenticated"))
                return
            
            headers = {"Authorization": f"Bearer {app.user_token}"}
            response = requests.get(f"{self.backend_url}/api/leads/", headers=headers, timeout=10)
            
            if response.status_code == 200:
                leads = response.json()
                Clock.schedule_once(lambda dt: self.display_leads(leads))
            else:
                Clock.schedule_once(lambda dt: self.show_error("Failed to load leads"))
                
        except Exception as e:
            Clock.schedule_once(lambda dt: self.show_error(f"Error: {str(e)}"))
    
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
        
        # Update stats
        self.total_leads_label.text = f"Total: {len(leads)}"
        new_count = len([l for l in leads if l.get('status') == 'new'])
        qualified_count = len([l for l in leads if l.get('status') == 'qualified'])
        self.new_leads_label.text = f"New: {new_count}"
        self.qualified_leads_label.text = f"Qualified: {qualified_count}"
        
        for lead in leads:
            lead_card = self.create_enhanced_lead_card(lead)
            self.leads_container.add_widget(lead_card)
    
    def create_enhanced_lead_card(self, lead):
        """Create an enhanced card widget for a single lead."""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=180,  # Increased height to accommodate more content
            padding=20,
            spacing=8
        )
        
        # Card background with shadow effect
        with card.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            # Shadow
            Color(0, 0, 0, 0.1)
            card.shadow = RoundedRectangle(
                pos=(card.x + 2, card.y - 2),
                size=card.size,
                radius=[12]
            )
            # Main card
            Color(1, 1, 1, 1)
            card.rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[12])
            
            def update_rect(instance, value):
                card.rect.pos = instance.pos
                card.rect.size = instance.size
                card.shadow.pos = (instance.x + 2, instance.y - 2)
                card.shadow.size = instance.size
            
            card.bind(pos=update_rect, size=update_rect)
        
        # Header row with name and status
        header_row = BoxLayout(size_hint_y=None, height=30, spacing=10)
        
        name = f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip() or "Unnamed Lead"
        name_label = Label(
            text=name,
            font_size='18sp',
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
            halign='left',
            valign='middle',
            size_hint_x=0.7,
            text_size=(None, None),
            shorten=True,
            shorten_from='right'
        )
        name_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        
        # Status badge
        status = lead.get('status', 'new')
        status_colors = {
            'new': (0.2, 0.7, 0.3, 1),
            'contacted': (0.2, 0.5, 0.9, 1),
            'qualified': (0.6, 0.4, 0.9, 1),
            'proposal': (1, 0.6, 0, 1),
            'negotiation': (1, 0.4, 0, 1),
            'won': (0.1, 0.8, 0.2, 1),
            'lost': (0.8, 0.2, 0.2, 1)
        }
        status_color = status_colors.get(status, (0.5, 0.5, 0.5, 1))
        
        status_badge = Label(
            text=status.upper(),
            font_size='11sp',
            bold=True,
            color=status_color,
            size_hint_x=0.3,
            halign='right',
            valign='middle'
        )
        status_badge.bind(size=status_badge.setter('text_size'))
        
        header_row.add_widget(name_label)
        header_row.add_widget(status_badge)
        card.add_widget(header_row)
        
        # Title and Company row - FIXED with proper text wrapping
        title_company = lead.get('title', '')
        company = lead.get('company', '')
        if title_company and company:
            role_text = f"{title_company} at {company}"
        elif company:
            role_text = company
        elif title_company:
            role_text = title_company
        else:
            role_text = "No company info"
        
        role_label = Label(
            text=role_text,
            font_size='13sp',
            color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None,
            height=40,  # Increased to allow for two lines if needed
            halign='left',
            valign='top',
            text_size=(None, None),
            shorten=True,
            shorten_from='right',
            max_lines=2  # Allow text to wrap to 2 lines
        )
        role_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value - 10, None)))
        card.add_widget(role_label)
        
        # Contact info row
        contact_row = BoxLayout(size_hint_y=None, height=25, spacing=15)
        
        email = lead.get('email', 'No email')
        email_label = Label(
            text=f"📧 {email}",
            font_size='12sp',
            color=(0.3, 0.3, 0.3, 1),
            halign='left',
            valign='middle',
            size_hint_x=0.6,
            text_size=(None, None),
            shorten=True,
            shorten_from='center'  # Changed from 'middle' to 'center'
        )
        email_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        
        phone = lead.get('phone', '')
        if phone:
            phone_label = Label(
                text=f"📞 {phone}",
                font_size='12sp',
                color=(0.3, 0.3, 0.3, 1),
                halign='left',
                valign='middle',
                size_hint_x=0.4
            )
            phone_label.bind(size=phone_label.setter('text_size'))
            contact_row.add_widget(email_label)
            contact_row.add_widget(phone_label)
        else:
            email_label.size_hint_x = 1
            contact_row.add_widget(email_label)
        
        card.add_widget(contact_row)
        
        # Value and Priority row
        bottom_row = BoxLayout(size_hint_y=None, height=25)
        
        value = lead.get('value', 0)
        priority = lead.get('priority', 'medium')
        
        value_label = Label(
            text=f"💰 ${value:,.2f}" if value else "No value set",
            font_size='13sp',
            bold=True,
            color=(0.2, 0.6, 0.2, 1) if value else (0.5, 0.5, 0.5, 1),
            halign='left',
            valign='middle',
            size_hint_x=0.5
        )
        value_label.bind(size=value_label.setter('text_size'))
        
        priority_colors = {
            'high': (0.9, 0.2, 0.2, 1),
            'medium': (1, 0.6, 0, 1),
            'low': (0.5, 0.5, 0.5, 1)
        }
        priority_label = Label(
            text=f"Priority: {priority.upper()}",
            font_size='11sp',
            color=priority_colors.get(priority, (0.5, 0.5, 0.5, 1)),
            halign='right',
            valign='middle',
            size_hint_x=0.5
        )
        priority_label.bind(size=priority_label.setter('text_size'))
        
        bottom_row.add_widget(value_label)
        bottom_row.add_widget(priority_label)
        card.add_widget(bottom_row)
        
        return card
    
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
            text="Dashboard",
            font_size='28sp',
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
            halign='left',
            valign='middle'
        )
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
            {"title": "Working Prospects", "subtitle": "Manage your active prospects", "icon": "account-group", "screen": ""},
            {"title": "Follow-Up Tasks", "subtitle": "Track and complete follow-ups", "icon": "calendar-clock", "screen": ""},
            {"title": "Worksheets", "subtitle": "Buyer orders and deal packs", "icon": "file-document-outline", "screen": ""},
            {"title": "My Leads", "subtitle": "View and manage your leads", "icon": "account", "screen": "leads"},
            {"title": "Training Center", "subtitle": "Access training materials", "icon": "school", "screen": ""},
            {"title": "Goals & Accountability", "subtitle": "Track your sales goals", "icon": "flag-checkered", "screen": ""},
            {"title": "Notifications", "subtitle": "View your alerts and updates", "icon": "bell", "screen": ""},
            {"title": "Settings", "subtitle": "Manage your profile and preferences", "icon": "cog", "screen": ""},
        ]

        for item in dashboard_items:
            button = DashboardButton(
                title=item["title"],
                subtitle=item["subtitle"],
                icon=item["icon"],
                screen_name=item["screen"]
            )
            grid_layout.add_widget(button)

        root_layout.add_widget(grid_layout)
        self.add_widget(root_layout)

    def logout(self, instance):
        self.on_logout_callback()

class PhoenixCRMApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Orange"
        self.user_token = None
        self.screen_manager = ScreenManager()
        
        login_screen = LoginScreen(name='login', on_login_callback=self.on_login_success)
        self.screen_manager.add_widget(login_screen)
        
        dashboard_screen = DashboardScreen(name='dashboard', on_logout_callback=self.on_logout)
        self.screen_manager.add_widget(dashboard_screen)
        
        # Add leads screen
        leads_screen = LeadsScreen(name='leads')
        self.screen_manager.add_widget(leads_screen)
        
        return self.screen_manager

    def on_login_success(self, token):
        print(f"Login successful! Token: {token}")
        self.user_token = token
        self.screen_manager.current = 'dashboard'

    def on_logout(self):
        self.user_token = None
        self.screen_manager.current = 'login'

if __name__ == '__main__':
    try:
        PhoenixCRMApp().run()
    except Exception as e:
        print(f"Error starting Kivy application: {e}")
        sys.exit(1)
