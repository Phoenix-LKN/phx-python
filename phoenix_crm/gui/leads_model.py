"""
Lead data model and business logic for PhoenixCRM
"""
import threading
import requests
from typing import List, Dict, Callable, Optional
from kivy.clock import Clock


class LeadsModel:
    """Model class for managing lead data and API interactions."""
    
    def __init__(self, backend_url: str, token: str):
        self.backend_url = backend_url
        self.token = token
        self.leads = []
        self.filtered_leads = []
        self.search_query = ""
        self.filter_stage = "all"
        self.sort_by = "name"
        
    def fetch_leads(self, callback: Callable):
        """Fetch leads from backend in a separate thread."""
        thread = threading.Thread(target=self._fetch_leads_thread, args=(callback,), daemon=True)
        thread.start()
    
    def _fetch_leads_thread(self, callback: Callable):
        """Background thread for fetching leads."""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.backend_url}/api/leads/",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.leads = response.json()
                self.apply_filters()
                Clock.schedule_once(lambda dt: callback(True, self.filtered_leads))
            else:
                Clock.schedule_once(lambda dt: callback(False, "Failed to load leads"))
        except Exception as e:
            Clock.schedule_once(lambda dt: callback(False, str(e)))
    
    def apply_filters(self):
        """Apply search, filter, and sort to leads."""
        filtered = self.leads.copy()
        
        # Apply search
        if self.search_query:
            query = self.search_query.lower()
            filtered = [
                lead for lead in filtered
                if query in lead.get('first_name', '').lower()
                or query in lead.get('last_name', '').lower()
                or query in lead.get('email', '').lower()
                or query in lead.get('company', '').lower()
            ]
        
        # Apply stage filter
        if self.filter_stage != "all":
            filtered = [lead for lead in filtered if lead.get('status') == self.filter_stage]
        
        # Apply sorting
        if self.sort_by == "name":
            filtered.sort(key=lambda x: f"{x.get('first_name', '')} {x.get('last_name', '')}")
        elif self.sort_by == "value":
            filtered.sort(key=lambda x: x.get('value', 0), reverse=True)
        elif self.sort_by == "priority":
            priority_order = {'high': 0, 'medium': 1, 'low': 2}
            filtered.sort(key=lambda x: priority_order.get(x.get('priority', 'medium'), 1))
        elif self.sort_by == "stage":
            filtered.sort(key=lambda x: x.get('status', 'new'))
        
        self.filtered_leads = filtered
        return filtered
    
    def search_leads(self, query: str):
        """Update search query and reapply filters."""
        self.search_query = query
        return self.apply_filters()
    
    def filter_by_stage(self, stage: str):
        """Filter leads by stage."""
        self.filter_stage = stage
        return self.apply_filters()
    
    def sort_leads(self, sort_by: str):
        """Sort leads by specified field."""
        self.sort_by = sort_by
        return self.apply_filters()
    
    def get_stats(self) -> Dict:
        """Calculate lead statistics."""
        total = len(self.leads)
        new = len([l for l in self.leads if l.get('status') == 'new'])
        qualified = len([l for l in self.leads if l.get('status') == 'qualified'])
        
        return {
            'total': total,
            'new': new,
            'qualified': qualified,
        }
    
    def get_stage_groups(self) -> Dict[str, List]:
        """Group leads by stage for Kanban view."""
        stages = {
            'new': [],
            'contacted': [],
            'qualified': [],
            'proposal': [],
            'won': []
        }
        
        for lead in self.leads:
            stage = lead.get('status', 'new')
            if stage in stages:
                stages[stage].append(lead)
        
        return stages
