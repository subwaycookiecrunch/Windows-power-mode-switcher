import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import re
import ctypes
import sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class PowerModeSwitcher:
    def __init__(self):
        # Check for admin rights
        if not is_admin():
            messagebox.showerror(
                "Administrator Rights Required",
                "This application needs administrator rights to change power plans.\n\n"
                "Please right-click and select 'Run as administrator'."
            )
            sys.exit(1)
            
        self.root = tk.Tk()
        self.root.title("Power Mode Switcher")
        self.root.geometry("350x320")
        self.root.resizable(False, False)
        
        # Set window icon and style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure custom button styles
        self.configure_styles()
        
        # Get available power plans
        self.power_plans = self.get_power_plans()
        self.current_plan = self.get_active_plan()
        
        # Create UI elements
        self.create_ui()
        
        # Center window on screen
        self.center_window()
        
    def configure_styles(self):
        # Configure button styles
        self.style.configure(
            'High.TButton', 
            font=('Segoe UI', 11, 'bold'),
            background='#4CAF50',
            foreground='white'
        )
        
        self.style.configure(
            'Normal.TButton', 
            font=('Segoe UI', 11, 'bold'),
            background='#2196F3',
            foreground='white'
        )
        
        self.style.configure(
            'Battery.TButton', 
            font=('Segoe UI', 11, 'bold'),
            background='#FF9800',
            foreground='white'
        )
        
        self.style.configure(
            'Exit.TButton', 
            font=('Segoe UI', 10),
            background='#f0f0f0'
        )
        
        # Configure label styles
        self.style.configure(
            'Title.TLabel',
            font=('Segoe UI', 16, 'bold'),
            foreground='#333333'
        )
        
        self.style.configure(
            'Status.TLabel',
            font=('Segoe UI', 11),
            foreground='#555555'
        )
        
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_ui(self):
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="20 20 20 20")
        main_frame.pack(fill='both', expand=True)
        
        # Title Label
        title_label = ttk.Label(
            main_frame, 
            text="Windows Power Mode Switcher", 
            style='Title.TLabel'
        )
        title_label.pack(pady=(0, 20))
        
        # Current status
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill='x', pady=(0, 15))
        
        status_label = ttk.Label(
            status_frame, 
            text="Current Power Plan:", 
            style='Status.TLabel'
        )
        status_label.pack(side='left')
        
        self.current_plan_label = ttk.Label(
            status_frame, 
            text=self.current_plan if self.current_plan else "Unknown",
            style='Status.TLabel',
            font=('Segoe UI', 11, 'bold')
        )
        self.current_plan_label.pack(side='left', padx=(5, 0))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='both', expand=True)
        
        # High Performance Button
        high_perf_btn = ttk.Button(
            buttons_frame,
            text="High Performance",
            command=self.set_high_performance,
            style='High.TButton',
            width=30
        )
        high_perf_btn.pack(pady=8, ipady=8)
        
        # Balanced Button
        balanced_btn = ttk.Button(
            buttons_frame,
            text="Balanced (Normal)",
            command=self.set_balanced,
            style='Normal.TButton',
            width=30
        )
        balanced_btn.pack(pady=8, ipady=8)
        
        # Power Saver Button
        power_saver_btn = ttk.Button(
            buttons_frame,
            text="Power Saver (Battery)",
            command=self.set_power_saver,
            style='Battery.TButton',
            width=30
        )
        power_saver_btn.pack(pady=8, ipady=8)
        
        # Exit Button
        exit_btn = ttk.Button(
            main_frame,
            text="Exit",
            command=self.root.quit,
            style='Exit.TButton',
            width=15
        )
        exit_btn.pack(pady=(15, 0))
        
    def get_power_plans(self):
        try:
            # Run powercfg /list to get all power plans
            result = subprocess.run(
                ['powercfg', '/list'], 
                capture_output=True, 
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            plans = {}
            for line in result.stdout.split('\n'):
                if 'Power Scheme GUID' in line:
                    # Extract GUID and name using regex for better reliability
                    guid_match = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', line)
                    name_match = re.search(r'\(([^\)]*)\)', line)
                    
                    if guid_match and name_match:
                        guid = guid_match.group(1)
                        name = name_match.group(1)
                        plans[name] = guid
            
            return plans
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get power plans: {str(e)}\n\nPlease run as administrator.")
            return {}
    
    def get_active_plan(self):
        try:
            # Get the active power plan
            result = subprocess.run(
                ['powercfg', '/getactivescheme'], 
                capture_output=True, 
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Extract the name using regex
            name_match = re.search(r'\(([^\)]*)\)', result.stdout)
            if name_match:
                return name_match.group(1)
            return None
        except Exception:
            return None
        
    def set_power_plan(self, plan_name):
        try:
            # Find the plan by partial name match if exact match fails
            matching_plans = [name for name in self.power_plans.keys() 
                             if plan_name.lower() in name.lower()]
            
            if matching_plans:
                # Use the first matching plan
                name = matching_plans[0]
                guid = self.power_plans[name]
                
                # Set the power plan
                subprocess.run(
                    ['powercfg', '/setactive', guid],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                # Update the current plan display
                self.current_plan = name
                self.current_plan_label.config(text=name)
                
                # Show success message
                messagebox.showinfo("Success", f"Switched to {name} mode")
            else:
                messagebox.showerror(
                    "Error", 
                    f"Power plan '{plan_name}' not found.\n\n"
                    f"Available plans: {', '.join(self.power_plans.keys())}"
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set power plan: {str(e)}\n\nPlease run as administrator.")
        
    def set_high_performance(self):
        self.set_power_plan("High performance")
        
    def set_balanced(self):
        self.set_power_plan("Balanced")
        
    def set_power_saver(self):
        self.set_power_plan("Power saver")
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = PowerModeSwitcher()
    app.run()
