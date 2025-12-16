"""
Status GUI implementation using tkinter (cross-platform, built-in)
Provides visual dashboard for DUT status monitoring
"""
from __future__ import annotations

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    # Test if tkinter actually works
    test_root = tk.Tk()
    test_root.withdraw()  # Hide the test window
    test_root.destroy()
    TKINTER_AVAILABLE = True
except (ImportError, Exception):
    TKINTER_AVAILABLE = False
    tk = None
    ttk = None
    messagebox = None
import threading
import time
import json
import io
import os
from contextlib import redirect_stdout
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

import click


@dataclass 
class DUTInfo:
    """DUT information structure with usage tracking"""
    dut_id: str
    status: str = "Unknown"
    response_time: float = 0.0
    nets_count: int = 0
    last_seen: str = "Unknown"
    nets: list = None
    locked_by: Optional[str] = None
    lock_status: str = "Unlocked"
    session_duration: Optional[str] = None
    usage_history: list = None
    last_user: Optional[str] = None
    
    def __post_init__(self):
        if self.nets is None:
            self.nets = []
        if self.usage_history is None:
            self.usage_history = []


class StatusGUI:
    """Status dashboard GUI application"""
    
    def __init__(self, ctx, dut: Optional[str], refresh_interval: float, emitter):
        self.ctx = ctx
        self.target_dut = dut
        self.refresh_interval = refresh_interval
        self.emitter = emitter
        self.running = False
        self.refresh_thread = None
        
        # Data storage
        self.dut_data: Dict[str, DUTInfo] = {}
        self.selected_dut: Optional[str] = None  # Will be set to first DUT after data load
        self.all_duts: List[str] = []
        
        # Create main window
        self.root = tk.Tk()
        self.root.title(f"Lager Status Dashboard - DUT {dut}")
        self.root.geometry("1200x800")  # Larger window for better readability
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.minsize(800, 600)  # Minimum window size
        
        # Enhanced Lager color scheme with better contrast and readability
        self.colors = {
            'bg_dark': '#1e1e1e',      # Slightly lighter dark background
            'bg_light': '#2d2d2d',     # Lighter dark background  
            'bg_card': '#3a3a3a',      # More contrast for card background
            'accent': '#ff69b4',       # Lager pink
            'accent_hover': '#ff1493', # Darker pink for hover states
            'text_primary': '#ffffff',  # White text
            'text_secondary': '#cccccc', # Lighter gray text for better readability
            'text_muted': '#999999',   # Muted text for less important info
            'success': '#28a745',      # Professional green for success
            'error': '#dc3545',        # Professional red for error
            'warning': '#ffc107',      # Professional yellow for warning
            'info': '#17a2b8',         # Professional blue for info
            'border': '#555555',       # Border color for separation
            'header_bg': '#2a2a2a'     # Header background
        }
        
        # Configure root window
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure custom styles for Lager theme
        self.configure_styles()
        
        # Configure colors for status
        self.status_colors = {
            "Online": self.colors['success'],
            "Offline": self.colors['error'],
            "Error": self.colors['warning'], 
            "Unknown": self.colors['text_secondary']
        }
        
        self.setup_ui()
    
    def configure_styles(self):
        """Configure custom ttk styles for Lager theme"""
        # Configure frame styles
        self.style.configure('Dark.TFrame', 
                           background=self.colors['bg_dark'])
        self.style.configure('Card.TFrame',
                           background=self.colors['bg_card'],
                           relief='flat',
                           borderwidth=1)
        
        # Configure label styles with better contrast and spacing
        self.style.configure('Title.TLabel',
                           background=self.colors['bg_dark'],
                           foreground=self.colors['text_primary'],
                           font=('Segoe UI', 22, 'bold'))  # Larger, better font
        self.style.configure('Header.TLabel',
                           background=self.colors['bg_card'],
                           foreground=self.colors['accent'],
                           font=('Segoe UI', 13, 'bold'))
        self.style.configure('Dark.TLabel',
                           background=self.colors['bg_dark'],
                           foreground=self.colors['text_primary'],
                           font=('Segoe UI', 10))
        self.style.configure('Card.TLabel',
                           background=self.colors['bg_card'],
                           foreground=self.colors['text_primary'],
                           font=('Segoe UI', 10))
        self.style.configure('Subtitle.TLabel',
                           background=self.colors['bg_dark'],
                           foreground=self.colors['text_secondary'],
                           font=('Segoe UI', 11))
        self.style.configure('Status.TLabel',
                           background=self.colors['bg_card'],
                           foreground=self.colors['text_secondary'],
                           font=('Segoe UI', 9))
        
        # Configure button styles with better appearance
        self.style.configure('Accent.TButton',
                           background=self.colors['accent'],
                           foreground='white',
                           borderwidth=0,
                           focuscolor='none',
                           font=('Segoe UI', 10, 'bold'),
                           padding=(15, 8))  # Better padding
        self.style.map('Accent.TButton',
                     background=[('active', self.colors['accent_hover']),
                               ('pressed', self.colors['accent_hover'])])  # Better hover states
        
        # Configure notebook styles
        self.style.configure('Dark.TNotebook',
                           background=self.colors['bg_card'],
                           borderwidth=0)
        self.style.configure('Dark.TNotebook.Tab',
                           background=self.colors['bg_light'],
                           foreground=self.colors['text_primary'],
                           padding=[20, 8])
        self.style.map('Dark.TNotebook.Tab',
                     background=[('selected', self.colors['accent']),
                               ('active', self.colors['bg_card'])])
        
        # Configure treeview styles with better readability
        self.style.configure('Dark.Treeview',
                           background=self.colors['bg_light'],
                           foreground=self.colors['text_primary'],
                           fieldbackground=self.colors['bg_light'],
                           borderwidth=1,
                           relief='solid',
                           font=('Segoe UI', 10),
                           rowheight=28)  # Better row spacing
        self.style.configure('Dark.Treeview.Heading',
                           background=self.colors['header_bg'],
                           foreground=self.colors['text_primary'],
                           borderwidth=1,
                           relief='solid',
                           font=('Segoe UI', 10, 'bold'))
        self.style.map('Dark.Treeview',
                     background=[('selected', self.colors['accent']),
                               ('focus', self.colors['accent'])],
                     foreground=[('selected', 'white'),
                               ('focus', 'white')])
        
    def setup_ui(self):
        """Setup the user interface with enhanced spacing and layout"""
        # Main container with dark theme and better padding
        main_frame = ttk.Frame(self.root, style='Dark.TFrame', padding="25")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Header section with logo and title
        header_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        header_frame.columnconfigure(1, weight=1)
        
        # Try to load and display Lager logo
        logo_loaded = False
        try:
            import os
            import sys

            # Try multiple paths to find the logo
            possible_paths = [
                "assets/logo.png",  # Relative to current working directory
                "/Users/danielerskine/Desktop/LagerData/Internship2025/lager-cli/assets/logo.png",  # Absolute path
            ]

            # Also try relative to the module file
            try:
                module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                project_root = os.path.dirname(module_dir)
                possible_paths.append(os.path.join(project_root, 'assets', 'logo.png'))
            except:
                pass

            # Try bundled executable path
            if hasattr(sys, '_MEIPASS'):
                possible_paths.insert(0, os.path.join(sys._MEIPASS, 'assets', 'logo.png'))

            logo_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    logo_path = path
                    break

            if logo_path:
                self.logo_photo = tk.PhotoImage(file=logo_path)
                # Subsample the image to make it smaller (since PhotoImage doesn't have resize)
                self.logo_photo = self.logo_photo.subsample(4, 4)  # Reduce size
                logo_label = ttk.Label(header_frame, image=self.logo_photo, style='Dark.TLabel')
                logo_label.grid(row=0, column=0, padx=(0, 15))
                logo_loaded = True
        except Exception as e:
            pass

        if not logo_loaded:
            # Fallback: Pink square to match Lager branding
            logo_canvas = tk.Canvas(header_frame, width=60, height=60,
                                  bg=self.colors['accent'], highlightthickness=0)
            logo_canvas.grid(row=0, column=0, padx=(0, 15))
        
        # Title and subtitle
        title_frame = ttk.Frame(header_frame, style='Dark.TFrame')
        title_frame.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        title_label = ttk.Label(title_frame, text="Lager Status Dashboard", style='Title.TLabel')
        title_label.pack(anchor=tk.W)
        
        # Get current user info for subtitle
        try:
            current_user = self._get_current_user()
            subtitle_text = f"Logged in as: {current_user} • Hardware Testing Dashboard"
        except Exception:
            subtitle_text = "Hardware Testing Dashboard • Session Active"
            
        subtitle_label = ttk.Label(title_frame, 
                                 text=subtitle_text,
                                 style='Subtitle.TLabel')
        subtitle_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Create main content area with splitter
        content_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Left panel: Multi-DUT overview
        self.setup_multi_dut_overview(content_frame)
        
        # Right panel: Selected DUT details  
        self.setup_dut_details_panel(content_frame)
        
        # Control panel at bottom (read-only monitoring controls)
        self.setup_monitoring_controls(main_frame)
        
        # Enhanced status bar with better styling
        self.status_var = tk.StringVar(value="Initializing...")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W, style='Status.TLabel',
                              padding=(10, 5))  # Better padding
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def create_status_cards(self, parent):
        """Create modern status cards"""
        self.overview_labels = {}
        
        # Status cards data
        cards = [
            ("Target DUT", self.target_dut or "All"),
            ("Backend", "Connected"), 
            ("Last Update", "Never"),
            ("Auto-refresh", f"Every {self.refresh_interval}s")
        ]
        
        for i, (title, value) in enumerate(cards):
            # Card frame
            card = ttk.Frame(parent, style='Card.TFrame', padding="15")
            card.grid(row=0, column=i, padx=(0, 15 if i < len(cards)-1 else 0), 
                     sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Card header without icon
            title_label = ttk.Label(card, text=title, style='Header.TLabel')
            title_label.pack(anchor=tk.W)
            
            # Card value
            value_label = ttk.Label(card, text=value, style='Card.TLabel',
                                  font=('Arial', 12, 'bold'))
            value_label.pack(anchor=tk.W, pady=(10, 0))
            
            self.overview_labels[f"{title}:"] = value_label

    def setup_multi_dut_overview(self, parent):
        """Setup left panel with multi-DUT overview"""
        # Left panel for DUT overview
        left_panel = ttk.Frame(parent, style='Card.TFrame', padding="15")
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_panel.rowconfigure(1, weight=1)
        
        # Header
        header_label = ttk.Label(left_panel, text="All DUTs", style='Header.TLabel')
        header_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # DUT overview table
        columns = ("dut_id", "status", "lock_status", "response_time", "nets", "last_user")
        self.dut_overview_tree = ttk.Treeview(left_panel, columns=columns, show="headings", 
                                            height=12, style='Dark.Treeview')
        
        # Configure columns for multi-DUT view
        column_configs = {
            "dut_id": ("DUT ID", 80),
            "status": ("Status", 80),
            "lock_status": ("Lock Status", 100),
            "response_time": ("Response", 80),
            "nets": ("Nets", 50),
            "last_user": ("Last User", 180)
        }
        
        for col, (heading, width) in column_configs.items():
            self.dut_overview_tree.heading(col, text=heading)
            self.dut_overview_tree.column(col, width=width, minwidth=width)
        
        # Scrollbar for DUT table
        dut_scrollbar = ttk.Scrollbar(left_panel, orient=tk.VERTICAL, 
                                    command=self.dut_overview_tree.yview)
        self.dut_overview_tree.configure(yscrollcommand=dut_scrollbar.set)
        
        # Pack table and scrollbar
        self.dut_overview_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        dut_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # Bind selection event
        self.dut_overview_tree.bind('<<TreeviewSelect>>', self.on_dut_selected)
        
    def setup_dut_details_panel(self, parent):
        """Setup right panel with detailed DUT information"""
        # Right panel for selected DUT details
        right_panel = ttk.Frame(parent, style='Card.TFrame', padding="15")
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)
        
        # Header with selected DUT info
        self.selected_dut_header = ttk.Label(right_panel, 
                                           text="Select a DUT for details", 
                                           style='Header.TLabel')
        self.selected_dut_header.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Create notebook for detailed tabs
        self.notebook = ttk.Notebook(right_panel, style='Dark.TNotebook')
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Setup detail tabs
        self.setup_usage_history_tab()
        self.setup_networks_tab()
        self.setup_activity_log_tab()
        
    def setup_monitoring_controls(self, parent):
        """Setup read-only monitoring controls"""
        control_frame = ttk.Frame(parent, style='Dark.TFrame')
        control_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Monitoring controls (read-only)
        monitor_label = ttk.Label(control_frame, text="Monitoring Controls:", 
                                style='Header.TLabel', font=('Arial', 10, 'bold'))
        monitor_label.pack(side=tk.LEFT)
        
        # Auto-refresh toggle (read-only monitoring)
        self.auto_refresh_var = tk.BooleanVar(value=True)
        auto_refresh_cb = ttk.Checkbutton(control_frame, text="Auto-refresh", 
                                        variable=self.auto_refresh_var,
                                        command=self.toggle_auto_refresh)
        self.style.configure('TCheckbutton',
                           background=self.colors['bg_dark'],
                           foreground=self.colors['text_primary'],
                           focuscolor=self.colors['accent'])
        auto_refresh_cb.pack(side=tk.LEFT, padx=(10, 0))
        
        # Manual refresh button
        self.refresh_btn = ttk.Button(control_frame, text="Refresh Now", 
                                     style='Accent.TButton',
                                     command=self.manual_refresh)
        self.refresh_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Status indicator
        self.status_var = tk.StringVar(value="Starting monitoring...")
        status_label = ttk.Label(control_frame, textvariable=self.status_var,
                               style='Dark.TLabel', font=('Arial', 10, 'italic'))
        status_label.pack(side=tk.RIGHT)
        
    def on_dut_selected(self, event):
        """Handle DUT selection from overview table"""
        selection = self.dut_overview_tree.selection()
        if selection:
            item = self.dut_overview_tree.item(selection[0])
            selected_dut_id = item['values'][0]  # First column is DUT ID
            self.selected_dut = selected_dut_id
            self.update_selected_dut_details()
            
    def update_selected_dut_details(self):
        """Update the details panel for selected DUT"""
        if not self.selected_dut or self.selected_dut not in self.dut_data:
            self.selected_dut_header.configure(text="Select a DUT for details")
            return
            
        dut_info = self.dut_data[self.selected_dut]
        header_text = f"DUT {self.selected_dut} Details"
        if dut_info.lock_status != "Unlocked":
            header_text += f" - {dut_info.lock_status}"
        
        self.selected_dut_header.configure(text=header_text)
        self.update_usage_history()
        self.update_networks_display()

    def setup_usage_history_tab(self):
        """Setup usage history and lock status tab"""
        usage_frame = ttk.Frame(self.notebook, style='Card.TFrame')
        self.notebook.add(usage_frame, text="Usage History")
        
        # Current lock status section
        lock_frame = ttk.LabelFrame(usage_frame, text="Current Status", padding="10")
        lock_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.lock_status_label = ttk.Label(lock_frame, text="Status: Unlocked", 
                                         style='Card.TLabel', font=('Arial', 11, 'bold'))
        self.lock_status_label.pack(anchor=tk.W)
        
        self.session_info_label = ttk.Label(lock_frame, text="No active session", 
                                          style='Card.TLabel')
        self.session_info_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Usage history table
        history_label = ttk.Label(usage_frame, text="Usage History", 
                                style='Header.TLabel', font=('Arial', 12, 'bold'))
        history_label.pack(anchor=tk.W, pady=(10, 5))
        
        # Usage history treeview
        history_columns = ("timestamp", "user", "action", "duration")
        self.usage_history_tree = ttk.Treeview(usage_frame, columns=history_columns, 
                                             show="headings", height=10, style='Dark.Treeview')
        
        history_column_configs = {
            "timestamp": ("Timestamp", 150),
            "user": ("User", 100),
            "action": ("Action", 100),
            "duration": ("Duration", 100)
        }
        
        for col, (heading, width) in history_column_configs.items():
            self.usage_history_tree.heading(col, text=heading)
            self.usage_history_tree.column(col, width=width)
        
        # History scrollbar
        history_scrollbar = ttk.Scrollbar(usage_frame, orient=tk.VERTICAL, 
                                        command=self.usage_history_tree.yview)
        self.usage_history_tree.configure(yscrollcommand=history_scrollbar.set)
        
        self.usage_history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_networks_tab(self):
        """Setup networks tab for selected DUT"""
        net_frame = ttk.Frame(self.notebook, style='Card.TFrame')
        self.notebook.add(net_frame, text="Nets")
        
        # Create treeview for networks of selected DUT
        columns = ("net_name", "net_type", "instrument", "channel", "status")
        self.selected_net_tree = ttk.Treeview(net_frame, columns=columns, show="headings", 
                                            height=10, style='Dark.Treeview')
        
        # Configure columns
        column_configs = {
            "net_name": ("Net Name", 120),
            "net_type": ("Type", 80),
            "instrument": ("Instrument", 150),
            "channel": ("Channel", 100),
            "status": ("Status", 80)
        }
        
        for col, (heading, width) in column_configs.items():
            self.selected_net_tree.heading(col, text=heading)
            self.selected_net_tree.column(col, width=width)
        
        # Scrollbar for networks table
        net_scrollbar = ttk.Scrollbar(net_frame, orient=tk.VERTICAL, 
                                    command=self.selected_net_tree.yview)
        self.selected_net_tree.configure(yscrollcommand=net_scrollbar.set)
        
        self.selected_net_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        net_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def update_usage_history(self):
        """Update usage history for selected DUT"""
        if not self.selected_dut or self.selected_dut not in self.dut_data:
            return
            
        dut_info = self.dut_data[self.selected_dut]
        
        # Update lock status
        if dut_info.locked_by:
            status_text = f"Status: Locked by {dut_info.locked_by}"
            session_text = f"Session duration: {dut_info.session_duration or 'Unknown'}"
        else:
            status_text = "Status: Unlocked"
            session_text = "No active session"
            
        self.lock_status_label.configure(text=status_text)
        self.session_info_label.configure(text=session_text)
        
        # Update usage history table
        self.usage_history_tree.delete(*self.usage_history_tree.get_children())
        for entry in dut_info.usage_history:
            self.usage_history_tree.insert('', tk.END, values=(
                entry.get('timestamp', ''),
                entry.get('user', ''),
                entry.get('action', ''),
                entry.get('duration', '')
            ))
            
    def update_networks_display(self):
        """Update networks display for selected DUT"""
        if not self.selected_dut or self.selected_dut not in self.dut_data:
            return
            
        dut_info = self.dut_data[self.selected_dut]
        
        # Clear and repopulate networks table
        self.selected_net_tree.delete(*self.selected_net_tree.get_children())
        for net in dut_info.nets:
            net_status = "Active" if dut_info.status == "Online" else "Unknown"
            self.selected_net_tree.insert('', tk.END, values=(
                net.get("name", "Unknown"),
                net.get("role", "Unknown"), 
                net.get("instrument", "None"),
                net.get("pin", "N/A"),
                net_status
            ))

    
    def setup_activity_log_tab(self):
        """Setup activity log tab"""
        log_frame = ttk.Frame(self.notebook, style='Card.TFrame')
        self.notebook.add(log_frame, text="Activity Log")
        
        # Create text widget for log with enhanced dark theme and better formatting
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, height=15,
                               bg=self.colors['bg_light'],
                               fg=self.colors['text_primary'],
                               insertbackground=self.colors['accent'],
                               selectbackground=self.colors['accent'],
                               font=('Consolas', 12),  # Increased font size for better readability
                               relief='solid',
                               borderwidth=1,
                               padx=10, pady=8)  # Internal padding for better readability
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        # Pack text and scrollbar
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure text tags for better colored output
        self.log_text.tag_config("info", foreground=self.colors['info'])
        self.log_text.tag_config("success", foreground=self.colors['success'])
        self.log_text.tag_config("warning", foreground=self.colors['warning'])
        self.log_text.tag_config("error", foreground=self.colors['error'])

    
    def log_message(self, message: str, level: str = "info"):
        """Add formatted message to activity log with better structure"""
        timestamp = time.strftime("%H:%M:%S")
        
        # Format the message with better visual structure
        level_prefix = {
            "info": "ℹ",
            "success": "✓",
            "warning": "⚠",
            "error": "✗"
        }.get(level, "•")
        
        full_message = f"[{timestamp}] {level_prefix} {message}\n"
        
        # Insert with proper formatting and color
        self.log_text.insert(tk.END, full_message, level)
        self.log_text.see(tk.END)
        
        # Keep log size manageable - keep last 500 lines
        line_count = int(self.log_text.index('end-1c').split('.')[0])
        if line_count > 500:
            self.log_text.delete('1.0', f'{line_count - 400}.0')






    
    
    def fetch_dut_data(self):
        """Fetch real DUT data from backend for all configured DUTs"""
        try:
            from ..dut_storage import list_duts
            from .commands import _check_dut_connectivity, _get_dut_nets

            # Get all configured DUTs
            duts = list_duts()

            if not duts:
                self.log_message("No DUTs configured in .lager file", "warning")
                return False

            # Process each configured DUT
            for dut_name, dut_info_raw in duts.items():
                # Handle both string (IP only) and dict formats
                if isinstance(dut_info_raw, dict):
                    dut_ip = dut_info_raw.get('ip', dut_info_raw.get('address', 'unknown'))
                else:
                    dut_ip = dut_info_raw

                if dut_ip == 'unknown':
                    continue

                self.log_message(f"Fetching data for DUT {dut_name} ({dut_ip})", "info")

                # Check DUT connectivity using the fixed function
                connectivity_result = _check_dut_connectivity(dut_ip)
                status = connectivity_result['status']
                response_time = connectivity_result['response_time'] / 1000.0  # Convert ms to seconds

                if status == "Online":
                    self.log_message(f"DUT {dut_name}: Online (response time: {response_time:.3f}s)", "success")
                elif status == "Offline":
                    self.log_message(f"DUT {dut_name}: Offline - {connectivity_result.get('error', 'Unknown error')}", "error")
                else:
                    self.log_message(f"DUT {dut_name}: {status} - {connectivity_result.get('error', 'Unknown error')}", "warning")
                # Get nets data (only if DUT is online)
                if status == "Online":
                    nets_info = _get_dut_nets(self.ctx, dut_ip)
                    nets_data = nets_info.get('nets', [])
                    if nets_info.get('error'):
                        self.log_message(f"DUT {dut_name}: Error fetching nets - {nets_info['error']}", "error")
                    else:
                        self.log_message(f"DUT {dut_name}: Found {len(nets_data)} nets", "success")
                else:
                    nets_data = []

                # Get real user information from JWT token
                try:
                    current_user = self._get_current_user()
                    # For now, use simple lock status - in real implementation this would come from lock status API
                    lock_status = "Unlocked"  # Would come from real lock status API
                    locked_by = None
                    session_duration = None

                    self.log_message(f"DUT {dut_name}: Current user - {current_user}", "info")

                except Exception as e:
                    current_user = "unknown@user.com"
                    lock_status = "Unknown"
                    locked_by = None
                    session_duration = None
                    self.log_message(f"DUT {dut_name}: Error getting user info - {e}", "warning")

                # Update DUT info with real data (use DUT name for display)
                self.dut_data[dut_name] = DUTInfo(
                    dut_id=dut_name,
                    status=status,
                    response_time=response_time,
                    nets_count=len(nets_data),
                    last_seen=time.strftime("%H:%M:%S"),
                    nets=nets_data,
                    locked_by=locked_by,
                    lock_status=lock_status,
                    session_duration=session_duration,
                    usage_history=[],  # Real usage history would come from backend API
                    last_user=current_user
                )

                # Emit events for consistency
                self.emitter.emit('dut_status', {
                    'dut_id': dut_name,
                    'status': status,
                    'response_time': response_time,
                    'nets_count': len(nets_data)
                })

            self.log_message(f"Successfully updated {len(duts)} DUTs with real data", "success")
            return True
            
        except Exception as e:
            self.log_message(f"Error fetching real DUT data: {e}", "error")
            return False
    
    def _parse_backend_json(self, raw: str):
        """
        Parse JSON response from backend, handling duplicate output from double execution.

        Args:
            raw: Raw output from backend

        Returns:
            Parsed JSON data

        Raises:
            json.JSONDecodeError: If JSON cannot be parsed
        """
        try:
            return json.loads(raw or "[]")
        except json.JSONDecodeError:
            # Handle duplicate JSON output from backend double execution
            if raw and raw.count('[') >= 2:
                # Try to extract the first JSON array
                depth = 0
                first_array_end = -1
                for i, char in enumerate(raw):
                    if char == '[':
                        depth += 1
                    elif char == ']':
                        depth -= 1
                        if depth == 0:
                            first_array_end = i + 1
                            break

                if first_array_end > 0:
                    first_json = raw[:first_array_end]
                    return json.loads(first_json)
                else:
                    raise json.JSONDecodeError("Could not find complete JSON array", raw, 0)
            else:
                # Handle duplicate JSON objects (e.g., {"ok": true}{"ok": true})
                if raw and raw.count('{') >= 2:
                    depth = 0
                    first_obj_end = -1
                    for i, char in enumerate(raw):
                        if char == '{':
                            depth += 1
                        elif char == '}':
                            depth -= 1
                            if depth == 0:
                                first_obj_end = i + 1
                                break

                    if first_obj_end > 0:
                        first_json = raw[:first_obj_end]
                        return json.loads(first_json)

                raise  # Re-raise original exception

    def _get_current_user(self):
        """Extract current user information from userinfo endpoint"""
        try:
            from ..auth import load_auth, get_auth_url
            import jwt
            import requests
            
            auth = load_auth()
            if auth and 'token' in auth:
                # Try userinfo endpoint first (same as whoami command)
                try:
                    userinfo_url = f"{get_auth_url()}/userinfo"
                    headers = {'Authorization': f'Bearer {auth["token"]}'}
                    resp = requests.get(userinfo_url, headers=headers, timeout=5)
                    
                    if resp.status_code == 200:
                        user_info = resp.json()
                        # Return email if available
                        if 'email' in user_info:
                            return user_info['email']
                        elif 'name' in user_info:
                            return user_info['name']
                        elif 'nickname' in user_info:
                            return user_info['nickname']
                except requests.RequestException:
                    # Fall through to token parsing if request fails
                    pass
                
                # Fallback to JWT token parsing
                decoded = jwt.decode(auth['token'], options={'verify_signature': False})
                
                # Try to get email or meaningful user identifier from token
                if 'email' in decoded:
                    return decoded['email']
                elif 'name' in decoded:
                    return decoded['name']
                elif 'nickname' in decoded:
                    return decoded['nickname']
                elif 'sub' in decoded:
                    # Auth0 subject - extract user ID part for cleaner display
                    sub = decoded['sub']
                    if '|' in sub:
                        user_id = sub.split('|')[1][:8]
                        return f"user_{user_id}"
                    return f"user_{sub[:8]}"
                else:
                    return "authenticated_user"
            else:
                return "no_auth"
                
        except Exception as e:
            return f"auth_error"
    
    def refresh_data(self):
        """Refresh all data and update displays"""
        try:
            self.status_var.set("Refreshing...")
            self.refresh_btn.configure(state="disabled")
            
            # Do the data fetching (now uses mock data to avoid blocking)
            success = self.fetch_dut_data()

            # Auto-select first DUT if none is selected
            if not self.selected_dut and self.dut_data:
                self.selected_dut = list(self.dut_data.keys())[0]
                self.log_message(f"Auto-selected DUT {self.selected_dut}", "info")

            # Update displays
            self.update_multi_dut_overview()
            self.update_selected_dut_details()
            
            if success:
                status_msg = f"Monitoring {len(self.dut_data)} DUTs - Last updated: {time.strftime('%H:%M:%S')}"
                self.status_var.set(status_msg)
                self.log_message("Data refresh completed successfully", "success")
            else:
                self.status_var.set("Update failed - using mock data")
                self.log_message("Data refresh failed, showing mock data", "warning")
                
        except Exception as e:
            error_msg = f"Refresh error: {str(e)}"
            self.log_message(error_msg, "error")
            self.status_var.set("Update failed - error occurred")
            
            # Show some data even on error to keep GUI functional
            if not self.dut_data:
                self.log_message("No data available, generating emergency mock data", "warning")
                self._generate_emergency_data()
                
        finally:
            # Always re-enable the button
            try:
                self.refresh_btn.configure(state="normal")
            except Exception:
                pass  # Ignore button state errors
    
    def _generate_emergency_data(self):
        """Generate minimal emergency data to keep GUI functional"""
        emergency_dut = self.target_dut or "DEMO"
        self.dut_data[emergency_dut] = DUTInfo(
            dut_id=emergency_dut,
            status="Emergency-Mode",
            response_time=0.0,
            nets_count=0,
            last_seen=time.strftime("%H:%M:%S"),
            nets=[],
            locked_by=None,
            lock_status="Unknown",
            session_duration=None,
            usage_history=[],
            last_user=None
        )
    
    def update_multi_dut_overview(self):
        """Update the multi-DUT overview table"""
        try:
            # Clear existing data
            self.dut_overview_tree.delete(*self.dut_overview_tree.get_children())
            
            # Populate with current DUT data
            for dut_id, dut_info in self.dut_data.items():
                # Format response time
                response_str = f"{dut_info.response_time:.3f}s" if dut_info.response_time < 999 else "Timeout"
                
                self.dut_overview_tree.insert('', tk.END, values=(
                    dut_info.dut_id,
                    dut_info.status,
                    dut_info.lock_status,
                    response_str,
                    dut_info.nets_count,
                    dut_info.last_user or "Unknown"
                ))
                
            self.log_message(f"Updated overview for {len(self.dut_data)} DUTs", "success")
            
        except Exception as e:
            self.log_message(f"Error updating multi-DUT overview: {e}", "error")
    
    def update_displays(self):
        """Update all display elements"""
        # The main displays are now handled by update_multi_dut_overview and update_selected_dut_details
        # which are called from refresh_data()
        pass
    
    def manual_refresh(self):
        """Handle manual refresh button"""
        self.refresh_data()
    
    def toggle_auto_refresh(self):
        """Toggle auto-refresh on/off"""
        if self.auto_refresh_var.get():
            self.start_auto_refresh()
            self.log_message("Auto-refresh enabled", "info")
        else:
            self.stop_auto_refresh()
            self.log_message("Auto-refresh disabled", "info")
    
    def start_auto_refresh(self):
        """Start auto-refresh using tkinter timer"""
        if not self.running:
            self.running = True
            self.schedule_next_refresh()
    
    def stop_auto_refresh(self):
        """Stop auto-refresh"""
        self.running = False
    
    def schedule_next_refresh(self):
        """Schedule next auto-refresh using tkinter timer"""
        if self.running and self.auto_refresh_var.get():
            # Schedule refresh in main thread after interval
            self.root.after(int(self.refresh_interval * 1000), self.auto_refresh_callback)
    
    def auto_refresh_callback(self):
        """Auto-refresh callback - runs in main thread"""
        try:
            self.refresh_data()
            self.schedule_next_refresh()  # Schedule next refresh
        except Exception as e:
            self.log_message(f"Auto-refresh error: {e}", "error")
    
    def on_closing(self):
        """Handle window closing"""
        self.stop_auto_refresh()
        self.emitter.emit('gui_close', {'reason': 'user_close'})
        self.root.destroy()
    
    def run(self):
        """Run the GUI application"""
        self.log_message("Status GUI started", "success")
        
        # Initial data load
        self.refresh_data()
        
        # Start auto-refresh if enabled
        if self.auto_refresh_var.get():
            self.start_auto_refresh()
        
        # Start the GUI main loop
        self.root.mainloop()


def launch_status_gui(ctx: click.Context, dut: Optional[str], refresh_interval: float = 10.0) -> None:
    """Launch the status GUI"""
    from ..dut_storage import get_dut_ip

    # Resolve local DUT if provided
    if dut:
        local_ip = get_dut_ip(dut)
        if local_ip:
            dut = local_ip

    # Create a minimal emitter that doesn't do anything
    class DummyEmitter:
        def emit(self, event, data):
            pass

    emitter = DummyEmitter()
    ui_config = {}

    emitter.emit('gui_launch', {'dut': dut, 'refresh_interval': refresh_interval})
    
    if not TKINTER_AVAILABLE:
        emitter.emit('gui_error', {'error': 'tkinter not available', 'details': 'tkinter module not found'})
        click.secho("GUI not available: tkinter not working.", fg='yellow')
        click.secho("   This could be due to:", fg='yellow')
        click.secho("   1. Missing tkinter: brew install python-tk", fg='cyan')
        click.secho("   2. Virtual env using different Python version", fg='cyan')
        click.secho("   3. SSH session without display forwarding", fg='cyan')
        click.secho("   Try: --ui=tui for text-based interface", fg='green')
        return False
    
    try:
        # Create and run GUI
        gui = StatusGUI(ctx, dut, refresh_interval, emitter)
        gui.run()
        return True
        
    except Exception as e:
        emitter.emit('gui_error', {'error': 'GUI launch failed', 'details': str(e)})
        click.echo(f"GUI launch failed: {e}")
        return False