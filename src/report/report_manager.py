"""
Report manager for browser component analysis.

This module creates detailed reports showing component interaction data,
importance rankings, and time spent analysis.
"""

import tkinter as tk
from tkinter import ttk
import threading
import random


class ReportManager:
    """Manages analysis reports for browser component interactions."""
    
    def __init__(self):
        """Initialize the report manager."""
        self.report_window = None
        self.report_active = False
    
    def show_component_analysis_report(self):
        """Show the component analysis report when timer expires."""
        try:
            print("📊 Generating component analysis report...")
            
            # Create report in a separate thread to avoid blocking
            report_thread = threading.Thread(target=self._create_report_window, daemon=True)
            report_thread.start()
            
            print("✅ Component analysis report initiated")
            return True
            
        except Exception as e:
            print(f"❌ Error showing report: {e}")
            return False
    
    def _generate_mock_data(self):
        """Generate mock component data for the report."""
        components = [
            "Navigation Menu",
            "Search Bar", 
            "Main Content Area",
            "Sidebar",
            "Footer Links",
            "Header Logo",
            "Call-to-Action Button",
            "Image Gallery",
            "Social Media Links",
            "Contact Form",
            "Product List",
            "User Profile",
            "Shopping Cart",
            "Video Player",
            "Comments Section"
        ]
        
        # Generate random data for each component
        component_data = []
        for i, name in enumerate(random.sample(components, 8)):  # Show 8 components
            component_data.append({
                'name': name,
                'importance': random.randint(1, 10),
                'time_spent': round(random.uniform(5.2, 45.8), 1),
                'score': random.randint(65, 98)
            })
        
        # Sort by importance (descending)
        component_data.sort(key=lambda x: x['importance'], reverse=True)
        return component_data
    
    def _create_report_window(self):
        """Create and display the analysis report window."""
        try:
            # Create a new root window for the report
            self.report_window = tk.Tk()
            self.report_window.title("Component Analysis Report")
            
            # Configure report window - optimized size for data table
            self.report_window.geometry("600x400")
            self.report_window.configure(bg='#f8f9fa')  # Light gray background
            
            # Make report always on top
            self.report_window.attributes('-topmost', True)
            
            # Center the report on screen
            self.report_window.update_idletasks()
            width = 600
            height = 400
            x = (self.report_window.winfo_screenwidth() // 2) - (width // 2)
            y = (self.report_window.winfo_screenheight() // 2) - (height // 2)
            self.report_window.geometry(f'{width}x{height}+{x}+{y}')
            
            # Create main container
            main_frame = tk.Frame(self.report_window, bg='#f8f9fa')
            main_frame.pack(expand=True, fill='both', padx=15, pady=15)
            
            # Report Header
            header_frame = tk.Frame(main_frame, bg='#f8f9fa')
            header_frame.pack(fill='x', pady=(0, 20))
            
            title_label = tk.Label(
                header_frame,
                text="📊 Component Analysis Report",
                font=('Arial', 14, 'bold'),
                fg='#2c3e50',
                bg='#f8f9fa'
            )
            title_label.pack()
            
            subtitle_label = tk.Label(
                header_frame,
                text="Browser session completed - Here's what we found:",
                font=('Arial', 9),
                fg='#7f8c8d',
                bg='#f8f9fa'
            )
            subtitle_label.pack(pady=(3, 0))
            
            # Generate mock data
            component_data = self._generate_mock_data()
            
            # Create table frame
            table_frame = tk.Frame(main_frame, bg='#ffffff', relief='solid', bd=1)
            table_frame.pack(fill='both', expand=True, pady=(0, 20))
            
            # Create scrollable table
            canvas = tk.Canvas(table_frame, bg='#ffffff', highlightthickness=0)
            scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='#ffffff')
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Table headers
            headers = ["Component Name", "Importance Rank", "Time Spent (s)", "Interaction Score"]
            header_colors = ['#34495e', '#e74c3c', '#3498db', '#27ae60']
            
            for col, (header, color) in enumerate(zip(headers, header_colors)):
                header_label = tk.Label(
                    scrollable_frame,
                    text=header,
                    font=('Arial', 10, 'bold'),
                    fg='white',
                    bg=color,
                    padx=8,
                    pady=6,
                    relief='solid',
                    bd=1
                )
                header_label.grid(row=0, column=col, sticky='ew')
            
            # Table data rows
            for row, data in enumerate(component_data, 1):
                # Alternate row colors
                row_color = '#ffffff' if row % 2 == 1 else '#ecf0f1'
                
                # Component name
                name_label = tk.Label(
                    scrollable_frame,
                    text=data['name'],
                    font=('Arial', 9),
                    fg='#2c3e50',
                    bg=row_color,
                    padx=8,
                    pady=5,
                    relief='solid',
                    bd=1,
                    anchor='w'
                )
                name_label.grid(row=row, column=0, sticky='ew')
                
                # Importance rank with color coding
                rank_color = '#e74c3c' if data['importance'] >= 8 else '#f39c12' if data['importance'] >= 6 else '#95a5a6'
                rank_label = tk.Label(
                    scrollable_frame,
                    text=f"#{data['importance']}",
                    font=('Arial', 9, 'bold'),
                    fg='white',
                    bg=rank_color,
                    padx=8,
                    pady=5,
                    relief='solid',
                    bd=1
                )
                rank_label.grid(row=row, column=1, sticky='ew')
                
                # Time spent
                time_label = tk.Label(
                    scrollable_frame,
                    text=f"{data['time_spent']}s",
                    font=('Arial', 9),
                    fg='#2c3e50',
                    bg=row_color,
                    padx=8,
                    pady=5,
                    relief='solid',
                    bd=1
                )
                time_label.grid(row=row, column=2, sticky='ew')
                
                # Score with color coding
                score_color = '#27ae60' if data['score'] >= 90 else '#f39c12' if data['score'] >= 75 else '#e74c3c'
                score_label = tk.Label(
                    scrollable_frame,
                    text=f"{data['score']}%",
                    font=('Arial', 9, 'bold'),
                    fg='white',
                    bg=score_color,
                    padx=8,
                    pady=5,
                    relief='solid',
                    bd=1
                )
                score_label.grid(row=row, column=3, sticky='ew')
            
            # Configure column weights for equal distribution
            for col in range(4):
                scrollable_frame.columnconfigure(col, weight=1)
            
            # Pack scrollable elements
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Summary stats frame
            stats_frame = tk.Frame(main_frame, bg='#ecf0f1', relief='solid', bd=1)
            stats_frame.pack(fill='x', pady=(0, 20))
            
            # Calculate summary stats
            total_time = sum(item['time_spent'] for item in component_data)
            avg_score = sum(item['score'] for item in component_data) / len(component_data)
            top_component = max(component_data, key=lambda x: x['importance'])
            
            stats_text = f"📈 Summary: {len(component_data)} components analyzed • Total time: {total_time:.1f}s • Average score: {avg_score:.1f}% • Top component: {top_component['name']}"
            
            stats_label = tk.Label(
                stats_frame,
                text=stats_text,
                font=('Arial', 8),
                fg='#2c3e50',
                bg='#ecf0f1',
                padx=10,
                pady=6
            )
            stats_label.pack()
            
            # Buttons frame
            buttons_frame = tk.Frame(main_frame, bg='#f8f9fa')
            buttons_frame.pack(fill='x')
            
            # Close button
            close_btn = tk.Button(
                buttons_frame,
                text="Close Report",
                font=('Arial', 9, 'bold'),
                bg='#3498db',
                fg='white',
                padx=20,
                pady=6,
                command=self._close_report
            )
            close_btn.pack(side='right')
            
            # Export button (placeholder)
            export_btn = tk.Button(
                buttons_frame,
                text="Export Data",
                font=('Arial', 9),
                bg='#95a5a6',
                fg='white',
                padx=20,
                pady=6,
                command=lambda: print("📁 Export functionality coming soon...")
            )
            export_btn.pack(side='right', padx=(0, 8))
            
            # Set report as active
            self.report_active = True
            
            # Handle window close button
            self.report_window.protocol("WM_DELETE_WINDOW", self._close_report)
            
            # Start the report event loop
            self.report_window.mainloop()
            
        except Exception as e:
            print(f"Error creating report window: {e}")
    
    def _close_report(self):
        """Close the report window."""
        try:
            if self.report_window:
                self.report_window.destroy()
                self.report_window = None
            self.report_active = False
            print("📋 Component analysis report closed")
        except Exception as e:
            print(f"Error closing report: {e}")
    
    def is_report_active(self):
        """Check if a report is currently active."""
        return self.report_active
    
    def close_any_active_report(self):
        """Close any currently active report."""
        if self.report_active:
            self._close_report()