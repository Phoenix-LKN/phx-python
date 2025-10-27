"""
Phoenix CRM - Main Application File
"""
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Register custom fonts BEFORE importing any Kivy/KivyMD modules
try:
    from gui.fonts import *
except Exception as e:
    print(f"⚠️  Warning: Could not load custom fonts: {e}")
    print("   The app will use system default fonts.")

# Now import Kivy modules
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.text import LabelBase

# Import all screens
from gui.screens.login_screen import LoginScreen
from gui.screens.new_dashboard import NewDashboardScreen
from gui.screens.settings_screen import SettingsScreen
from gui.screens.analytics_screen import AnalyticsScreen
from gui.screens.leads_screen import LeadsScreen
from gui.screens.worksheets_screen import WorksheetsScreen
from gui.screens.training_screen import TrainingScreen
from gui.screens.notifications_screen import NotificationsScreen
from gui.screens.appointments_screen import AppointmentsScreen
from gui.screens.goal_tracking_screen import GoalTrackingScreen
from gui.screens.help_screen import HelpScreen
from gui.screens.feedback_screen import FeedbackScreen
from gui.screens.privacy_policy_screen import PrivacyPolicyScreen
from gui.screens.terms_of_service_screen import TermsOfServiceScreen

# Define the window size for the application
Window.size = (360, 640)

# Load KV files
Builder.load_file('gui/kivy_files/login_screen.kv')
Builder.load_file('gui/kivy_files/new_dashboard.kv')
Builder.load_file('gui/kivy_files/settings_screen.kv')
Builder.load_file('gui/kivy_files/analytics_screen.kv')
Builder.load_file('gui/kivy_files/leads_screen.kv')
Builder.load_file('gui/kivy_files/worksheets_screen.kv')
Builder.load_file('gui/kivy_files/training_screen.kv')
Builder.load_file('gui/kivy_files/notifications_screen.kv')
Builder.load_file('gui/kivy_files/appointments_screen.kv')
Builder.load_file('gui/kivy_files/goal_tracking_screen.kv')
Builder.load_file('gui/kivy_files/help_screen.kv')
Builder.load_file('gui/kivy_files/feedback_screen.kv')
Builder.load_file('gui/kivy_files/privacy_policy_screen.kv')
Builder.load_file('gui/kivy_files/terms_of_service_screen.kv')


class PhoenixCRMApp(App):
    """Main application class for Phoenix CRM."""
    
    def build(self):
        """Build the app interface."""
        sm = ScreenManager()
        
        # Add all screens to the manager
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(NewDashboardScreen(name='dashboard', on_logout_callback=self.logout))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(AnalyticsScreen(name='analytics'))
        sm.add_widget(LeadsScreen(name='leads'))
        sm.add_widget(WorksheetsScreen(name='worksheets'))
        sm.add_widget(TrainingScreen(name='training'))
        sm.add_widget(NotificationsScreen(name='notifications'))
        sm.add_widget(AppointmentsScreen(name='appointments'))
        sm.add_widget(GoalTrackingScreen(name='goal_tracking'))
        sm.add_widget(HelpScreen(name='help'))
        sm.add_widget(FeedbackScreen(name='feedback'))
        sm.add_widget(PrivacyPolicyScreen(name='privacy_policy'))
        sm.add_widget(TermsOfServiceScreen(name='terms_of_service'))
        
        return sm
    
    def on_start(self):
        """App startup actions."""
        # Schedule a function to run after the app has started
        Clock.schedule_once(self.check_login_status, 1)
    
    def check_login_status(self, dt):
        """Check if the user is already logged in."""
        from kivy.core.window import Window
        Window.clearcolor = (1, 1, 1, 1)  # White background
        
        # For now, just go to the dashboard directly
        self.root.current = 'dashboard'
    
    def logout(self):
        """Handle user logout."""
        # For now, just go back to the login screen
        self.root.current = 'login'


if __name__ == '__main__':
    PhoenixCRMApp().run()