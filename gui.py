import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, date, timedelta
import calendar
from typing import Dict, List
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

from database import DatabaseManager
from habit_manager import HabitManager

class ModernHabitTrackerGUI:
    """Modern GUI class for the Habit Tracker application."""
    
    def __init__(self):
        """Initialize the GUI application."""
        self.root = tk.Tk()
        self.root.title("Habit Tracker - Modern UI")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f8f9fa')
        
        # Initialize database and habit manager
        self.db_manager = DatabaseManager()
        if not self.db_manager.connect():
            messagebox.showerror("Database Error", 
                               "Could not connect to database. Please check your MySQL configuration.")
            self.root.destroy()
            return
        
        self.habit_manager = HabitManager(self.db_manager)
        
        # Current month and year
        self.current_date = datetime.now()
        self.current_year = self.current_date.year
        self.current_month = self.current_date.month
        
        # GUI variables
        self.habits = []
        self.checkboxes = {}  # {(habit_id, day): checkbox_var}
        
        # Setup modern styling
        self.setup_styles()
        self.setup_gui()
        self.refresh_habits()
        self.update_calendar()
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_styles(self):
        """Setup modern styling for the application."""
        style = ttk.Style()
        
        # Configure styles
        style.theme_use('clam')
        
        # Modern color scheme
        colors = {
            'bg': '#f8f9fa',
            'fg': '#212529',
            'primary': '#007bff',
            'success': '#28a745',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40'
        }
        
        # Configure button styles
        style.configure('Primary.TButton',
                       background=colors['primary'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(15, 8))
        
        style.configure('Success.TButton',
                       background=colors['success'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(10, 6))
        
        style.configure('Danger.TButton',
                       background=colors['danger'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(10, 6))
    
    def setup_gui(self):
        """Set up the modern GUI layout."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header section
        self.setup_header(main_frame)
        
        # Content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Left panel - Habits list
        self.setup_habits_panel(content_frame)
        
        # Right panel - Calendar and charts
        self.setup_main_panel(content_frame)
    
    def setup_header(self, parent):
        """Set up the modern header section."""
        # Header frame with primary color
        header_frame = tk.Frame(parent, bg='#007bff', relief=tk.SOLID, bd=1)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Header content
        header_content = tk.Frame(header_frame, bg='#007bff')
        header_content.pack(fill=tk.X, padx=20, pady=15)
        
        # App title
        title_label = tk.Label(header_content, 
                              text="🎯 Habit Tracker", 
                              font=("Arial", 24, "bold"),
                              fg='white',
                              bg='#007bff')
        title_label.pack(side=tk.LEFT)
        
        # Month navigation on the right
        nav_frame = tk.Frame(header_content, bg='#007bff')
        nav_frame.pack(side=tk.RIGHT)
        
        tk.Button(nav_frame, text="‹", command=self.previous_month,
                 bg='#0056b3', fg='white', bd=0, padx=10, pady=5,
                 font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        
        self.month_label = tk.Label(nav_frame, 
                                   font=("Arial", 16, "bold"),
                                   fg='white',
                                   bg='#007bff')
        self.month_label.pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(nav_frame, text="›", command=self.next_month,
                 bg='#0056b3', fg='white', bd=0, padx=10, pady=5,
                 font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        
        # Refresh button
        tk.Button(nav_frame, text="🔄 Refresh", command=self.refresh_all,
                 bg='#28a745', fg='white', bd=0, padx=10, pady=5,
                 font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=(15, 0))
        
        self.update_month_label()
    
    def setup_habits_panel(self, parent):
        """Set up the left panel with habits list."""
        # Left panel frame
        left_panel = tk.Frame(parent, bg='white', relief=tk.SOLID, bd=1)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        left_panel.configure(width=300)
        left_panel.pack_propagate(False)
        
        # Header with add button
        habits_header = tk.Frame(left_panel, bg='white')
        habits_header.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        tk.Label(habits_header, text="My Habits", 
                font=("Arial", 16, "bold"),
                bg='white').pack(side=tk.LEFT)
        
        # Add habit button with plus icon
        add_btn = tk.Button(habits_header, text="➕ Add Habit", 
                           command=self.add_habit,
                           bg='#28a745', fg='white', bd=0,
                           padx=10, pady=5, font=("Arial", 10, "bold"))
        add_btn.pack(side=tk.RIGHT)
        
        # Separator
        tk.Frame(left_panel, height=1, bg='#dee2e6').pack(fill=tk.X, padx=15)
        
        # Scrollable habits list
        habits_canvas = tk.Canvas(left_panel, bg='white', highlightthickness=0)
        habits_scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=habits_canvas.yview)
        self.habits_list_frame = tk.Frame(habits_canvas, bg='white')
        
        self.habits_list_frame.bind(
            "<Configure>",
            lambda e: habits_canvas.configure(scrollregion=habits_canvas.bbox("all"))
        )
        
        habits_canvas.create_window((0, 0), window=self.habits_list_frame, anchor="nw")
        habits_canvas.configure(yscrollcommand=habits_scrollbar.set)
        
        habits_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=(10, 15))
        habits_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(10, 15), padx=(0, 15))
    
    def setup_main_panel(self, parent):
        """Set up the main content panel."""
        # Right panel frame
        right_panel = ttk.Frame(parent)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(right_panel)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Calendar tab
        self.calendar_frame = ttk.Frame(notebook)
        notebook.add(self.calendar_frame, text="📅 Calendar View")
        self.setup_calendar_tab()
        
        # Charts tab
        self.charts_frame = ttk.Frame(notebook)
        notebook.add(self.charts_frame, text="📊 Progress Charts")
        self.setup_charts_tab()
    
    def refresh_habits_list(self):
        """Refresh the habits list in the left panel."""
        # Clear existing habit widgets
        for widget in self.habits_list_frame.winfo_children():
            widget.destroy()
        
        if not self.habits:
            no_habits_label = tk.Label(self.habits_list_frame, 
                                     text="No habits yet.\nClick '➕ Add Habit' to start!",
                                     font=("Arial", 11),
                                     fg='#6c757d',
                                     bg='white',
                                     justify=tk.CENTER)
            no_habits_label.pack(pady=20)
            return
        
        # Create habit cards
        for habit in self.habits:
            self.create_habit_card(habit)
    
    def create_habit_card(self, habit):
        """Create a modern card for each habit."""
        # Main card frame
        card_frame = tk.Frame(self.habits_list_frame, 
                            bg='#f8f9fa', 
                            relief=tk.SOLID, 
                            bd=1)
        card_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Habit info frame
        info_frame = tk.Frame(card_frame, bg='#f8f9fa')
        info_frame.pack(fill=tk.X, padx=10, pady=8)
        
        # Habit name
        name_label = tk.Label(info_frame, 
                            text=habit['name'],
                            font=("Arial", 12, "bold"),
                            bg='#f8f9fa',
                            fg='#212529')
        name_label.pack(anchor=tk.W)
        
        # Habit description (if exists)
        if habit.get('description'):
            desc_label = tk.Label(info_frame,
                                text=habit['description'],
                                font=("Arial", 10),
                                bg='#f8f9fa',
                                fg='#6c757d',
                                wraplength=250)
            desc_label.pack(anchor=tk.W, pady=(2, 0))
        
        # Buttons frame
        buttons_frame = tk.Frame(info_frame, bg='#f8f9fa')
        buttons_frame.pack(anchor=tk.W, pady=(5, 0))
        
        # Edit button
        edit_btn = tk.Button(buttons_frame,
                           text="✏️ Edit",
                           font=("Arial", 9),
                           bg='#17a2b8',
                           fg='white',
                           bd=0,
                           padx=8,
                           pady=2,
                           command=lambda h=habit: self.edit_habit(h))
        edit_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Delete button
        delete_btn = tk.Button(buttons_frame,
                             text="🗑️ Delete",
                             font=("Arial", 9),
                             bg='#dc3545',
                             fg='white',
                             bd=0,
                             padx=8,
                             pady=2,
                             command=lambda h=habit: self.delete_habit(h))
        delete_btn.pack(side=tk.LEFT)
    
    def refresh_habits(self):
        """Refresh habits from database."""
        self.habits = self.habit_manager.get_habits()
        self.refresh_habits_list()
    
    def refresh_all(self):
        """Refresh all data including habits and calendar."""
        self.refresh_habits()
        self.update_calendar()
        self.update_chart()
        messagebox.showinfo("Refreshed", "✅ Data refreshed successfully!")
    
    def update_month_label(self):
        """Update the month label display."""
        month_name = calendar.month_name[self.current_month]
        self.month_label.config(text=f"{month_name} {self.current_year}")
    
    def previous_month(self):
        """Navigate to previous month."""
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        
        self.update_month_label()
        self.update_calendar()
    
    def next_month(self):
        """Navigate to next month."""
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        
        self.update_month_label()
        self.update_calendar()
    
    def setup_calendar_tab(self):
        """Set up the calendar view tab."""
        # Create scrollable frame
        canvas = tk.Canvas(self.calendar_frame, bg='white')
        scrollbar = ttk.Scrollbar(self.calendar_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg='white')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def setup_charts_tab(self):
        """Set up the charts view tab."""
        # Charts control frame
        controls_frame = ttk.Frame(self.charts_frame)
        controls_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(controls_frame, text="Select Habit:", font=("Arial", 12)).pack(side=tk.LEFT, padx=(0, 10))
        
        self.habit_var = tk.StringVar()
        self.habit_dropdown = ttk.Combobox(controls_frame, textvariable=self.habit_var, state="readonly", width=30)
        self.habit_dropdown.pack(side=tk.LEFT, padx=(0, 10))
        self.habit_dropdown.bind('<<ComboboxSelected>>', self.update_chart)
        
        # Chart frame
        self.chart_frame = ttk.Frame(self.charts_frame)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
    
    def update_calendar(self):
        """Update the modern calendar display."""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.checkboxes.clear()
        
        if not self.habits:
            no_habits_frame = tk.Frame(self.scrollable_frame, bg='white')
            no_habits_frame.pack(expand=True, fill=tk.BOTH)
            
            tk.Label(no_habits_frame, 
                    text="📝 No habits found!\n\nAdd your first habit using the '➕ Add Habit' button to get started.",
                    font=("Arial", 14),
                    fg='#6c757d',
                    bg='white',
                    justify=tk.CENTER).pack(expand=True)
            return
        
        # Update habits dropdown for charts
        habit_names = [f"{habit['name']} (ID: {habit['id']})" for habit in self.habits]
        self.habit_dropdown['values'] = habit_names
        if habit_names and not self.habit_var.get():
            self.habit_dropdown.set(habit_names[0])
        
        # Get number of days in current month
        days_in_month = calendar.monthrange(self.current_year, self.current_month)[1]
        
        # Create modern calendar header
        header_frame = tk.Frame(self.scrollable_frame, bg='#007bff', relief=tk.SOLID, bd=1)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 0))
        
        # Month title
        month_title = f"📅 {calendar.month_name[self.current_month].upper()} {self.current_year}"
        tk.Label(header_frame, 
                text=month_title, 
                font=("Arial", 18, "bold"),
                fg='white',
                bg='#007bff').pack(pady=15)
        
        # Calendar grid frame
        grid_frame = tk.Frame(self.scrollable_frame, bg='white', relief=tk.SOLID, bd=1)
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Days header - using proper grid layout
        days_header = tk.Frame(grid_frame, bg='#e9ecef')
        days_header.pack(fill=tk.X, pady=(0, 2))
        
        # Configure grid columns
        days_header.columnconfigure(0, weight=0, minsize=150)  # Habit name column
        for day in range(1, days_in_month + 1):
            days_header.columnconfigure(day, weight=0, minsize=35)  # Day columns
        days_header.columnconfigure(days_in_month + 1, weight=0, minsize=80)  # Total column
        
        # Create day headers
        tk.Label(days_header, text="HABIT", font=("Arial", 10, "bold"), 
                bg='#e9ecef', anchor='w').grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        for day in range(1, days_in_month + 1):
            day_label = tk.Label(days_header, 
                               text=str(day), 
                               font=("Arial", 9, "bold"),
                               bg='#e9ecef')
            day_label.grid(row=0, column=day, padx=2, pady=10, sticky="ew")
        
        # Total column
        tk.Label(days_header, text="TOTAL", font=("Arial", 10, "bold"), 
                bg='#e9ecef').grid(row=0, column=days_in_month + 1, padx=10, pady=10, sticky="ew")
        
        # Get month data
        month_data = self.habit_manager.get_month_data(self.current_year, self.current_month)
        
        # Create habit rows
        for row_idx, habit in enumerate(self.habits):
            self.create_habit_row(grid_frame, habit, row_idx, days_in_month, month_data)
    
    def create_habit_row(self, parent, habit, row_idx, days_in_month, month_data):
        """Create a modern row for each habit in the calendar."""
        habit_id = habit['id']
        habit_name = habit['name']
        completion_count = 0
        
        # Row frame with alternating colors
        row_bg = '#f8f9fa' if row_idx % 2 == 0 else 'white'
        row_frame = tk.Frame(parent, bg=row_bg, height=45)
        row_frame.pack(fill=tk.X, pady=1)
        row_frame.pack_propagate(False)
        
        # Configure grid columns to match header
        row_frame.columnconfigure(0, weight=0, minsize=150)  # Habit name column
        for day in range(1, days_in_month + 1):
            row_frame.columnconfigure(day, weight=0, minsize=35)  # Day columns
        row_frame.columnconfigure(days_in_month + 1, weight=0, minsize=80)  # Total column
        
        # Habit name
        name_label = tk.Label(row_frame, 
                            text=habit_name,
                            font=("Arial", 11),
                            bg=row_bg,
                            anchor='w')
        name_label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Checkboxes for each day
        for day in range(1, days_in_month + 1):
            var = tk.BooleanVar()
            is_completed = month_data.get(day, {}).get(habit_id, False)
            var.set(is_completed)
            
            if is_completed:
                completion_count += 1
            
            # Modern checkbox style
            checkbox = tk.Checkbutton(
                row_frame,
                variable=var,
                bg=row_bg,
                activebackground=row_bg,
                command=lambda h_id=habit_id, d=day, v=var: self.toggle_completion(h_id, d, v)
            )
            checkbox.grid(row=0, column=day, padx=2, pady=10, sticky="ew")
            
            self.checkboxes[(habit_id, day)] = var
        
        # Total count with modern styling
        total_label = tk.Label(row_frame, 
                             text=f"{completion_count}/{days_in_month}",
                             font=("Arial", 10, "bold"),
                             bg=row_bg,
                             fg='#007bff')
        total_label.grid(row=0, column=days_in_month + 1, padx=10, pady=10, sticky="ew")
    
    def toggle_completion(self, habit_id: int, day: int, var: tk.BooleanVar):
        """Toggle habit completion for a specific day."""
        completion_date = date(self.current_year, self.current_month, day)
        new_status = self.habit_manager.toggle_habit_completion(habit_id, completion_date)
        var.set(new_status)
        # Refresh the calendar to update totals
        self.update_calendar()
    
    def add_habit(self):
        """Add a new habit using modern dialog."""
        try:
            dialog = ModernHabitDialog(self.root, "Add New Habit")
            self.root.wait_window(dialog.dialog)  # Wait for dialog to close
            
            if dialog.result:
                name, description = dialog.result
                if self.habit_manager.add_new_habit(name, description):
                    messagebox.showinfo("Success", f"✅ Habit '{name}' added successfully!")
                    self.refresh_habits()
                    self.update_calendar()
                else:
                    messagebox.showerror("Error", "❌ Failed to add habit. Name might already exist.")
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error adding habit: {str(e)}")
    
    def edit_habit(self, habit):
        """Edit an existing habit using modern dialog."""
        try:
            dialog = ModernHabitDialog(self.root, "Edit Habit", habit['name'], habit.get('description', ''))
            self.root.wait_window(dialog.dialog)  # Wait for dialog to close
            
            if dialog.result:
                name, description = dialog.result
                if self.habit_manager.update_habit(habit['id'], name, description):
                    messagebox.showinfo("Success", f"✅ Habit '{name}' updated successfully!")
                    self.refresh_habits()
                    self.update_calendar()
                else:
                    messagebox.showerror("Error", "❌ Failed to update habit.")
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error editing habit: {str(e)}")
    
    def delete_habit(self, habit):
        """Delete a habit with confirmation."""
        if messagebox.askyesno("Confirm Delete", 
                             f"🗑️ Are you sure you want to delete '{habit['name']}'?\n\nThis will remove all progress data."):
            if self.habit_manager.delete_habit(habit['id']):
                messagebox.showinfo("Success", f"✅ Habit '{habit['name']}' deleted successfully!")
                self.refresh_habits()
                self.update_calendar()
            else:
                messagebox.showerror("Error", "❌ Failed to delete habit.")
    
    def update_chart(self, event=None):
        """Update the progress chart with modern line chart style."""
        # Clear existing chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        if not self.habits or not self.habit_var.get():
            return
        
        # Get selected habit ID
        selected_text = self.habit_var.get()
        try:
            habit_id = int(selected_text.split("ID: ")[1].split(")")[0])
        except:
            return
            
        habit = self.habit_manager.get_habit_by_id(habit_id)
        if not habit:
            return
        
        # Get habit data for the last 12 months
        try:
            chart_data = self.habit_manager.get_habit_chart_data(habit_id, 12)
        except Exception as e:
            tk.Label(self.chart_frame, 
                    text=f"Error loading chart data: {str(e)}",
                    font=("Arial", 12),
                    fg='red').pack(expand=True)
            return
        
        if not chart_data:
            tk.Label(self.chart_frame, 
                    text="No data available for this habit.",
                    font=("Arial", 12),
                    fg='#6c757d').pack(expand=True)
            return
        
        # Create modern line chart
        fig = Figure(figsize=(12, 6), dpi=100, facecolor='white')
        ax = fig.add_subplot(111)
        
        # Prepare data for plotting
        months = [data['month'] for data in chart_data]
        percentages = [data['percentage'] for data in chart_data]
        
        # Create modern line chart
        ax.plot(months, percentages, marker='o', linewidth=3, markersize=8, 
                color='#007bff', markerfacecolor='#007bff', markeredgecolor='white', 
                markeredgewidth=2, label='Completion %')
        
        # Fill area under the line
        ax.fill_between(months, percentages, alpha=0.2, color='#007bff')
        
        # Modern chart styling
        ax.set_title(f"📊 Progress for '{habit['name']}' - Last 12 Months",
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel("Month", fontsize=12)
        ax.set_ylabel("Completion Percentage (%)", fontsize=12)
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Rotate x-axis labels for better readability
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Add statistics text
        if chart_data:
            latest_data = chart_data[-1]
            stats_text = f"🎯 Latest Month: {latest_data['completions']}/{latest_data['total_days']} days ({latest_data['percentage']}%)"
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=11, 
                    verticalalignment='top', 
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='#e9ecef', alpha=0.8))
        
        # Adjust layout to prevent label cutoff
        fig.tight_layout()
        
        # Create canvas and add to frame
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def on_closing(self):
        """Handle application closing."""
        self.db_manager.close_connection()
        self.root.destroy()
    
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()


class ModernHabitDialog:
    """Modern dialog for adding/editing habits."""
    
    def __init__(self, parent, title, name="", description=""):
        """Initialize modern habit dialog."""
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x350")
        self.dialog.configure(bg='#f8f9fa')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 100, parent.winfo_rooty() + 100))
        
        # Header
        header_frame = tk.Frame(self.dialog, bg='#007bff', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(header_frame, 
                               text=f"🎯 {title}",
                               font=("Arial", 16, "bold"),
                               fg='white',
                               bg='#007bff')
        header_label.pack(expand=True)
        
        # Main content frame
        content_frame = tk.Frame(self.dialog, bg='#f8f9fa')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Name field
        tk.Label(content_frame, 
                text="Habit Name *",
                font=("Arial", 12, "bold"),
                bg='#f8f9fa',
                fg='#212529').pack(anchor=tk.W, pady=(0, 5))
        
        self.name_var = tk.StringVar(value=name)
        name_entry = tk.Entry(content_frame, 
                             textvariable=self.name_var,
                             font=("Arial", 11),
                             relief=tk.SOLID,
                             bd=1,
                             bg='white')
        name_entry.pack(fill=tk.X, pady=(0, 20), ipady=8)
        name_entry.focus()
        
        # Description field
        tk.Label(content_frame,
                text="Description (optional)",
                font=("Arial", 12, "bold"),
                bg='#f8f9fa',
                fg='#212529').pack(anchor=tk.W, pady=(0, 5))
        
        self.description_var = tk.StringVar(value=description)
        desc_entry = tk.Entry(content_frame,
                             textvariable=self.description_var,
                             font=("Arial", 11),
                             relief=tk.SOLID,
                             bd=1,
                             bg='white')
        desc_entry.pack(fill=tk.X, pady=(0, 30), ipady=8)
        
        # Buttons frame
        button_frame = tk.Frame(content_frame, bg='#f8f9fa')
        button_frame.pack(fill=tk.X)
        
        # Cancel button
        cancel_btn = tk.Button(button_frame,
                              text="❌ Cancel",
                              font=("Arial", 11),
                              bg='#6c757d',
                              fg='white',
                              bd=0,
                              padx=20,
                              pady=10,
                              command=self.cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Save button
        save_btn = tk.Button(button_frame,
                            text="✅ Save",
                            font=("Arial", 11, "bold"),
                            bg='#28a745',
                            fg='white',
                            bd=0,
                            padx=20,
                            pady=10,
                            command=self.save)
        save_btn.pack(side=tk.RIGHT)
        
        # Bind Enter and Escape keys
        self.dialog.bind('<Return>', lambda e: self.save())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
    
    def save(self):
        """Save the habit data."""
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "❌ Habit name is required!", parent=self.dialog)
            return
        
        self.result = (name, self.description_var.get().strip())
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel the dialog."""
        self.dialog.destroy()


if __name__ == "__main__":
    app = ModernHabitTrackerGUI()
    app.run()
