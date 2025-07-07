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

class HabitTrackerGUI:
    """Main GUI class for the Habit Tracker application."""
    
    def __init__(self):
        """Initialize the GUI application."""
        self.root = tk.Tk()
        self.root.title("Habit Tracker")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
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
        
        self.setup_gui()
        self.refresh_habits()
        self.update_calendar()
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_gui(self):
        """Set up the main GUI layout."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Header section
        self.setup_header(main_frame)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
        
        # Calendar tab
        self.calendar_frame = ttk.Frame(notebook)
        notebook.add(self.calendar_frame, text="Calendar View")
        self.setup_calendar_tab()
        
        # Charts tab
        self.charts_frame = ttk.Frame(notebook)
        notebook.add(self.charts_frame, text="Progress Charts")
        self.setup_charts_tab()
    
    def setup_header(self, parent):
        """Set up the header section with navigation and controls."""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)
        
        # Month navigation
        nav_frame = ttk.Frame(header_frame)
        nav_frame.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Button(nav_frame, text="◀", command=self.previous_month).pack(side=tk.LEFT, padx=(0, 5))
        
        self.month_label = ttk.Label(nav_frame, font=("Arial", 14, "bold"))
        self.month_label.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(nav_frame, text="▶", command=self.next_month).pack(side=tk.LEFT, padx=(0, 5))
        
        # Habit management buttons
        button_frame = ttk.Frame(header_frame)
        button_frame.grid(row=0, column=2, sticky=tk.E)
        
        ttk.Button(button_frame, text="Add Habit", command=self.add_habit).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(button_frame, text="Edit Habit", command=self.edit_habit).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(button_frame, text="Delete Habit", command=self.delete_habit).pack(side=tk.LEFT, padx=(5, 0))
        
        self.update_month_label()
    
    def setup_calendar_tab(self):
        """Set up the calendar view tab."""
        # Create scrollable frame
        canvas = tk.Canvas(self.calendar_frame, bg='white')
        scrollbar = ttk.Scrollbar(self.calendar_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def setup_charts_tab(self):
        """Set up the charts view tab."""
        # Chart selection frame
        chart_control_frame = ttk.Frame(self.charts_frame)
        chart_control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(chart_control_frame, text="Select Habit:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.habit_var = tk.StringVar()
        self.habit_combobox = ttk.Combobox(chart_control_frame, textvariable=self.habit_var, 
                                          state="readonly", width=30)
        self.habit_combobox.pack(side=tk.LEFT, padx=(0, 10))
        self.habit_combobox.bind('<<ComboboxSelected>>', self.update_chart)
        
        ttk.Button(chart_control_frame, text="Refresh Chart", 
                  command=self.update_chart).pack(side=tk.LEFT)
        
        # Chart frame
        self.chart_frame = ttk.Frame(self.charts_frame)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
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
        self.update_chart()
    
    def next_month(self):
        """Navigate to next month."""
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        
        self.update_month_label()
        self.update_calendar()
        self.update_chart()
    
    def refresh_habits(self):
        """Refresh the habits list from database."""
        self.habits = self.habit_manager.get_habits()
        
        # Update chart combobox
        if hasattr(self, 'habit_combobox'):
            habit_names = [f"{habit['name']} (ID: {habit['id']})" for habit in self.habits]
            self.habit_combobox['values'] = habit_names
            if habit_names and not self.habit_var.get():
                self.habit_combobox.set(habit_names[0])
    
    def update_calendar(self):
        """Update the calendar display with current month data."""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.checkboxes.clear()
        
        if not self.habits:
            ttk.Label(self.scrollable_frame, text="No habits found. Add a habit to get started!", 
                     font=("Arial", 12)).grid(row=0, column=0, padx=20, pady=20)
            return
        
        # Get number of days in current month
        days_in_month = calendar.monthrange(self.current_year, self.current_month)[1]
        
        # Create header row with day numbers
        ttk.Label(self.scrollable_frame, text="Habit", font=("Arial", 10, "bold")).grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        for day in range(1, days_in_month + 1):
            ttk.Label(self.scrollable_frame, text=str(day), font=("Arial", 9, "bold")).grid(
                row=0, column=day, padx=2, pady=5)
        
        # Get month data
        month_data = self.habit_manager.get_month_data(self.current_year, self.current_month)
        
        # Create rows for each habit
        for row_idx, habit in enumerate(self.habits, start=1):
            habit_id = habit['id']
            habit_name = habit['name']
            
            # Habit name label
            ttk.Label(self.scrollable_frame, text=habit_name, font=("Arial", 10)).grid(
                row=row_idx, column=0, padx=5, pady=2, sticky=tk.W)
            
            # Checkboxes for each day
            for day in range(1, days_in_month + 1):
                var = tk.BooleanVar()
                var.set(month_data.get(day, {}).get(habit_id, False))
                
                checkbox = tk.Checkbutton(
                    self.scrollable_frame,
                    variable=var,
                    command=lambda h_id=habit_id, d=day, v=var: self.toggle_completion(h_id, d, v)
                )
                checkbox.grid(row=row_idx, column=day, padx=2, pady=2)
                
                self.checkboxes[(habit_id, day)] = var
    
    def toggle_completion(self, habit_id: int, day: int, var: tk.BooleanVar):
        """Toggle habit completion for a specific day."""
        completion_date = date(self.current_year, self.current_month, day)
        new_status = self.habit_manager.toggle_habit_completion(habit_id, completion_date)
        var.set(new_status)
    
    def add_habit(self):
        """Add a new habit."""
        dialog = HabitDialog(self.root, "Add New Habit")
        if dialog.result:
            name, description = dialog.result
            if self.habit_manager.add_new_habit(name, description):
                messagebox.showinfo("Success", f"Habit '{name}' added successfully!")
                self.refresh_habits()
                self.update_calendar()
            else:
                messagebox.showerror("Error", "Failed to add habit. Name might already exist.")
    
    def edit_habit(self):
        """Edit an existing habit."""
        if not self.habits:
            messagebox.showwarning("No Habits", "No habits available to edit.")
            return
        
        # Select habit to edit
        habit_names = [f"{habit['name']} (ID: {habit['id']})" for habit in self.habits]
        selected = SelectionDialog(self.root, "Select Habit to Edit", habit_names).result
        
        if selected:
            habit_id = int(selected.split("ID: ")[1].split(")")[0])
            habit = self.habit_manager.get_habit_by_id(habit_id)
            
            if habit:
                dialog = HabitDialog(self.root, "Edit Habit", habit['name'], habit.get('description', ''))
                if dialog.result:
                    name, description = dialog.result
                    if self.habit_manager.update_habit(habit_id, name, description):
                        messagebox.showinfo("Success", "Habit updated successfully!")
                        self.refresh_habits()
                        self.update_calendar()
                    else:
                        messagebox.showerror("Error", "Failed to update habit.")
    
    def delete_habit(self):
        """Delete a habit."""
        if not self.habits:
            messagebox.showwarning("No Habits", "No habits available to delete.")
            return
        
        # Select habit to delete
        habit_names = [f"{habit['name']} (ID: {habit['id']})" for habit in self.habits]
        selected = SelectionDialog(self.root, "Select Habit to Delete", habit_names).result
        
        if selected:
            habit_id = int(selected.split("ID: ")[1].split(")")[0])
            habit = self.habit_manager.get_habit_by_id(habit_id)
            
            if habit:
                if messagebox.askyesno("Confirm Delete", 
                                     f"Are you sure you want to delete '{habit['name']}'?"):
                    if self.habit_manager.delete_habit(habit_id):
                        messagebox.showinfo("Success", "Habit deleted successfully!")
                        self.refresh_habits()
                        self.update_calendar()
                    else:
                        messagebox.showerror("Error", "Failed to delete habit.")
    
    def update_chart(self, event=None):
        """Update the progress chart."""
        # Clear existing chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        if not self.habits or not self.habit_var.get():
            return
        
        # Get selected habit ID
        selected_text = self.habit_var.get()
        habit_id = int(selected_text.split("ID: ")[1].split(")")[0])
        habit = self.habit_manager.get_habit_by_id(habit_id)
        
        if not habit:
            return
        
        # Get progress data
        progress_data = self.habit_manager.get_habit_progress_data(
            habit_id, self.current_year, self.current_month)
        
        # Create matplotlib figure
        fig = Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        # Prepare data for plotting
        days = [day for day, _ in progress_data]
        completions = [1 if completed else 0 for _, completed in progress_data]
        
        # Create bar chart
        bars = ax.bar(days, completions, color=['green' if c else 'lightcoral' for c in completions])
        
        # Customize chart
        ax.set_title(f"Progress for '{habit['name']}' - {calendar.month_name[self.current_month]} {self.current_year}")
        ax.set_xlabel("Day of Month")
        ax.set_ylabel("Completed (1) / Not Completed (0)")
        ax.set_ylim(0, 1.2)
        ax.set_xticks(days)
        ax.grid(True, alpha=0.3)
        
        # Add statistics
        stats = self.habit_manager.get_habit_statistics(habit_id, self.current_year, self.current_month)
        stats_text = f"Completion Rate: {stats['completion_rate']:.1f}% | Current Streak: {stats['current_streak']} days"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
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


class HabitDialog:
    """Dialog for adding/editing habits."""
    
    def __init__(self, parent, title, name="", description=""):
        """Initialize habit dialog."""
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Create form
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Name field
        ttk.Label(frame, text="Habit Name:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.name_var = tk.StringVar(value=name)
        name_entry = ttk.Entry(frame, textvariable=self.name_var, width=40)
        name_entry.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        name_entry.focus()
        
        # Description field
        ttk.Label(frame, text="Description (optional):").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.description_var = tk.StringVar(value=description)
        desc_entry = ttk.Entry(frame, textvariable=self.description_var, width=40)
        desc_entry.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, sticky="ew")
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT)
        
        # Configure grid
        frame.columnconfigure(0, weight=1)
        
        # Bind Enter and Escape keys
        self.dialog.bind('<Return>', lambda e: self.save())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
    
    def save(self):
        """Save the habit data."""
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Habit name is required!", parent=self.dialog)
            return
        
        self.result = (name, self.description_var.get().strip())
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel the dialog."""
        self.dialog.destroy()


class SelectionDialog:
    """Dialog for selecting from a list of options."""
    
    def __init__(self, parent, title, options):
        """Initialize selection dialog."""
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("300x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Create form
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Selection listbox
        ttk.Label(frame, text="Select an option:").pack(anchor=tk.W, pady=(0, 5))
        
        listbox_frame = ttk.Frame(frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        for option in options:
            self.listbox.insert(tk.END, option)
        
        if options:
            self.listbox.selection_set(0)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Select", command=self.select).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT)
        
        # Bind double-click and Enter
        self.listbox.bind('<Double-Button-1>', lambda e: self.select())
        self.dialog.bind('<Return>', lambda e: self.select())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
    
    def select(self):
        """Select the chosen option."""
        selection = self.listbox.curselection()
        if selection:
            self.result = self.listbox.get(selection[0])
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel the dialog."""
        self.dialog.destroy()


if __name__ == "__main__":
    app = HabitTrackerGUI()
    app.run()
