"""
Lead Drawer Component - Displays detailed lead information in a slide-in panel
"""
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.clock import Clock
import threading
import requests


class LeadDrawer(FloatLayout):
    """Slide-in drawer for displaying lead details."""
    
    def __init__(self, backend_url, token, on_close_callback, on_update_callback, **kwargs):
        super().__init__(**kwargs)
        self.backend_url = backend_url
        self.token = token
        self.on_close_callback = on_close_callback
        self.on_update_callback = on_update_callback
        self.lead_data = None
        self.is_open = False
        
        # Create overlay widget for dimmed background
        self.overlay = BoxLayout()
        self.overlay.opacity = 0
        
        with self.overlay.canvas.before:
            Color(0, 0, 0, 1)
            self.overlay._bg = Rectangle(pos=self.overlay.pos, size=self.overlay.size)
        self.overlay.bind(pos=lambda i, v: setattr(self.overlay._bg, 'pos', v))
        self.overlay.bind(size=lambda i, v: setattr(self.overlay._bg, 'size', v))
        
        self.add_widget(self.overlay)
        
        # Drawer panel container (initially off-screen to the right)
        self.drawer_panel = BoxLayout(
            orientation='vertical',
            size_hint=(None, 1),
            width=dp(400),
            padding=0,
            spacing=0,
            x=0,  # Start at 0, will be positioned properly in on_size
            y=0
        )
        
        # White background for drawer
        with self.drawer_panel.canvas.before:
            Color(1, 1, 1, 1)
            self.drawer_panel._bg = Rectangle(
                pos=self.drawer_panel.pos,
                size=self.drawer_panel.size
            )
            Color(0, 0, 0, 0.15)
            self.drawer_panel._shadow = Rectangle(
                pos=(self.drawer_panel.x - dp(5), self.drawer_panel.y),
                size=(dp(5), self.drawer_panel.height)
            )
        
        def update_drawer_bg(instance, value):
            instance._bg.pos = instance.pos
            instance._bg.size = instance.size
            instance._shadow.pos = (instance.x - dp(5), instance.y)
            instance._shadow.size = (dp(5), instance.height)
        
        self.drawer_panel.bind(pos=update_drawer_bg, size=update_drawer_bg)
        
        # Build drawer content
        self._build_drawer_content()
        
        self.add_widget(self.drawer_panel)
        
        # Bind to size changes to reposition drawer when window size changes
        self.bind(size=self._on_size)
        
        # Initially hide drawer off-screen (will be set properly in _on_size)
        Clock.schedule_once(lambda dt: self._hide_drawer(), 0.1)
    
    def _on_size(self, instance, value):
        """Handle size changes to reposition drawer."""
        if not self.is_open:
            self._hide_drawer()
    
    def _hide_drawer(self):
        """Position drawer off-screen to the right."""
        self.drawer_panel.x = self.width
        self.drawer_panel.y = 0
        self.drawer_panel.height = self.height
    
    def _build_drawer_content(self):
        """Build the drawer UI components."""
        from kivy.uix.scrollview import ScrollView
        
        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(0),
            padding=(dp(25), dp(20)),
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter('height'))
        
        # Close button at top
        close_row = BoxLayout(size_hint_y=None, height=dp(40))
        self.close_btn = Button(
            text="✕",
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            background_color=(0, 0, 0, 0),
            background_normal='',
            color=(0.3, 0.3, 0.3, 1),
            font_size='24sp'
        )
        self.close_btn.bind(on_press=lambda x: self.close())
        close_row.add_widget(self.close_btn)
        close_row.add_widget(Label())
        content.add_widget(close_row)
        
        # Name section
        self.name_label = Label(
            text="Lead Name",
            font_size='28sp',
            bold=True,
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=dp(40),
            halign='left',
            valign='top'
        )
        self.name_label.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
        content.add_widget(self.name_label)
        
        # Address section
        self.address_label = Label(
            text="Address",
            font_size='16sp',
            color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None,
            height=dp(60),
            halign='left',
            valign='top'
        )
        self.address_label.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
        content.add_widget(self.address_label)
        
        # Status badges row
        self.status_row = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )
        content.add_widget(self.status_row)
        
        # Divider
        content.add_widget(self._create_divider())
        
        # Related Property Section
        content.add_widget(self._create_section_header("Related Property"))
        self.property_content = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(100),
            padding=(0, dp(10))
        )
        content.add_widget(self.property_content)
        
        content.add_widget(self._create_divider())
        
        # Contact Info Section
        content.add_widget(self._create_section_header("Contact Info"))
        self.contact_content = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(80),
            spacing=dp(8),
            padding=(0, dp(10))
        )
        content.add_widget(self.contact_content)
        
        content.add_widget(self._create_divider())
        
        # Follow-Ups Section
        content.add_widget(self._create_section_header("Follow-Ups"))
        self.followups_content = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(80),
            spacing=dp(8),
            padding=(0, dp(10))
        )
        content.add_widget(self.followups_content)
        
        # Notes Section
        content.add_widget(Label(size_hint_y=None, height=dp(20)))
        content.add_widget(self._create_section_header("Notes"))
        self.notes_input = TextInput(
            text="",
            size_hint_y=None,
            height=dp(120),
            multiline=True,
            font_size='14sp',
            background_color=(0.97, 0.97, 0.97, 1),
            foreground_color=(0.2, 0.2, 0.2, 1),
            padding=(dp(15), dp(15))
        )
        content.add_widget(self.notes_input)
        
        # Action buttons
        content.add_widget(Label(size_hint_y=None, height=dp(20)))
        
        btn_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(180),
            spacing=dp(10)
        )
        
        # Add Note button
        add_note_btn = self._create_action_button("Add Note", outline=True)
        btn_container.add_widget(add_note_btn)
        
        # Set Follow-up Reminder button
        followup_btn = self._create_action_button("Set Follow-up Reminder", outline=True)
        btn_container.add_widget(followup_btn)
        
        # Mark as Interested button
        interested_btn = self._create_action_button("Mark as Interested", filled=True)
        btn_container.add_widget(interested_btn)
        
        content.add_widget(btn_container)
        
        scroll.add_widget(content)
        self.drawer_panel.add_widget(scroll)
    
    def _create_section_header(self, text):
        """Create a section header label."""
        header = Label(
            text=text or "",
            font_size='18sp',
            bold=True,
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=dp(30),
            halign='left',
            valign='middle'
        )
        header.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
        return header
    
    def _create_divider(self):
        """Create a divider line."""
        divider = Label(size_hint_y=None, height=dp(20))
        with divider.canvas.before:
            Color(0.9, 0.9, 0.9, 1)
            divider._line = Rectangle()
            divider.bind(
                pos=lambda i, v: setattr(i._line, 'pos', (i.x, i.y + dp(10))),
                size=lambda i, v: setattr(i._line, 'size', (i.width, 1))
            )
        return divider
    
    def _create_action_button(self, text, outline=False, filled=False):
        """Create an action button."""
        if filled:
            bg_color = (0, 0, 0, 1)
            text_color = (1, 1, 1, 1)
        else:
            bg_color = (1, 1, 1, 1)
            text_color = (0, 0, 0, 1)
        
        btn = Button(
            text=text or "",
            size_hint_y=None,
            height=dp(50),
            background_color=(0, 0, 0, 0),
            background_normal='',
            color=text_color,
            font_size='16sp',
            bold=True
        )
        
        with btn.canvas.before:
            if outline:
                Color(0.8, 0.8, 0.8, 1)
                btn._border = Rectangle()
            else:
                Color(*bg_color)
                btn._bg = Rectangle()
            
            btn.bind(
                pos=lambda i, v: setattr(i._border if outline else i._bg, 'pos', v),
                size=lambda i, v: setattr(i._border if outline else i._bg, 'size', v)
            )
        
        return btn
    
    def open(self, lead_data):
        """Open the drawer with lead data."""
        self.lead_data = lead_data
        self.is_open = True
        
        # Populate data
        self._populate_data()
        
        # Animate background dim - animate the overlay widget's opacity
        anim_bg = Animation(opacity=0.5, duration=0.3)
        anim_bg.start(self.overlay)
        
        # Calculate target position (drawer should slide in from the right)
        target_x = self.width - self.drawer_panel.width
        
        # Ensure drawer is at correct height
        self.drawer_panel.height = self.height
        
        # Animate drawer slide in
        anim_drawer = Animation(x=target_x, duration=0.3, t='out_expo')
        anim_drawer.start(self.drawer_panel)
        
        print(f"Opening drawer: target_x={target_x}, drawer_width={self.drawer_panel.width}, parent_width={self.width}")
    
    def close(self):
        """Close the drawer."""
        if not self.is_open:
            return
        
        self.is_open = False
        
        # Animate background - animate the overlay widget's opacity
        anim_bg = Animation(opacity=0, duration=0.3)
        anim_bg.start(self.overlay)
        
        # Animate drawer slide out to the right
        target_x = self.width
        anim_drawer = Animation(x=target_x, duration=0.3, t='in_expo')
        anim_drawer.bind(on_complete=lambda *args: self.on_close_callback())
        anim_drawer.start(self.drawer_panel)
        
        print(f"Closing drawer: target_x={target_x}")
    
    def _populate_data(self):
        """Populate drawer with lead data."""
        if not self.lead_data:
            return
        
        # Name - handle None values
        first_name = self.lead_data.get('first_name') or ''
        last_name = self.lead_data.get('last_name') or ''
        name = f"{first_name} {last_name}".strip()
        self.name_label.text = name or "Unnamed Lead"
        
        # Address
        company = self.lead_data.get('company') or ''
        email = self.lead_data.get('email') or ''
        self.address_label.text = f"{company}\n{email}" if company else email
        
        # Status badges
        self.status_row.clear_widgets()
        status = self.lead_data.get('status') or 'new'
        priority = self.lead_data.get('priority') or 'medium'
        
        self.status_row.add_widget(self._create_badge(status.title()))
        self.status_row.add_widget(self._create_badge(priority.title(), color=(0.7, 0.7, 0.7, 1)))
        self.status_row.add_widget(Label())  # Spacer
        
        # Contact info
        self.contact_content.clear_widgets()
        phone = self.lead_data.get('phone') or 'No phone'
        email = self.lead_data.get('email') or 'No email'
        
        self.contact_content.add_widget(self._create_info_row("📞", phone))
        self.contact_content.add_widget(self._create_info_row("📧", email))
        
        # Notes - handle None
        notes = self.lead_data.get('notes') or ''
        self.notes_input.text = notes
    
    def _create_badge(self, text, color=(0.92, 0.92, 0.92, 1)):
        """Create a status badge."""
        badge = Label(
            text=(text or "").upper(),
            size_hint=(None, None),
            size=(dp(100), dp(32)),
            font_size='12sp',
            bold=True,
            color=(0.3, 0.3, 0.3, 1)
        )
        
        with badge.canvas.before:
            Color(*color)
            badge._bg = Rectangle(
                pos=badge.pos,
                size=badge.size
            )
            badge.bind(
                pos=lambda i, v: setattr(i._bg, 'pos', v),
                size=lambda i, v: setattr(i._bg, 'size', v)
            )
        
        return badge
    
    def _create_info_row(self, icon, text):
        """Create an info row with icon and text."""
        row = BoxLayout(size_hint_y=None, height=dp(30), spacing=dp(10))
        
        icon_label = Label(
            text=icon or "",
            size_hint_x=None,
            width=dp(30),
            font_size='16sp'
        )
        
        text_label = Label(
            text=text or "",
            font_size='14sp',
            color=(0.3, 0.3, 0.3, 1),
            halign='left',
            valign='middle'
        )
        text_label.bind(width=lambda i, v: setattr(i, 'text_size', (v, None)))
        
        row.add_widget(icon_label)
        row.add_widget(text_label)
        
        return row
