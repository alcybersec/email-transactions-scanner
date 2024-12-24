"""
Email Transaction Scanner - A desktop app for viewing banking transactions from emails
Copyright (C) 2024 alcybersec

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import tkinter as tk
import customtkinter as ctk
from main import main, has_credentials
from datetime import datetime, timedelta
import re
import json
import os
from tkinter import ttk
from tkcalendar import Calendar
from functions_gui import ensure_settings_file, load_settings

# Set the theme and color scheme
ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), 'settings.json')
FONT_SIZE = 17  # Default font size for the application

class TransactionViewer(ctk.CTk):
    def __init__(self):
        super().__init__()
        ensure_settings_file()  # Replaces self.ensure_settings_file()
        
        self.title("Transaction Viewer")
        self.geometry("1080x720")
        
        # Main container with subtle gradient background
        main_container = ctk.CTkFrame(self, corner_radius=10)
        main_container.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Header with title - bigger font
        header = ctk.CTkLabel(
            main_container,
            text="Transaction Manager",
            font=ctk.CTkFont(size=28, weight="bold")  # Increased from 24
        )
        header.pack(pady=(0, 20))
        
        # Create notebook for tabs with modern styling
        self.notebook = ctk.CTkTabview(
            main_container,
            segmented_button_fg_color="#2B2B2B",  # Dark background for inactive tabs
            segmented_button_selected_color="#1F538D",  # Highlighted color for active tab
            segmented_button_selected_hover_color="#1A4574",  # Hover color for active tab
            segmented_button_unselected_color="#2B2B2B",  # Color for inactive tabs
            segmented_button_unselected_hover_color="#3B3B3B",  # Hover color for inactive tabs
            text_color="white"  # Text color
        )
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Create tabs with increased height for better visibility and font size
        self.notebook._segmented_button.configure(height=40, font=ctk.CTkFont(size=FONT_SIZE))
        self.notebook.add("Card Transactions")
        self.notebook.add("NEO Transactions")

        # Create styled tabs
        self.card_frame = ctk.CTkFrame(
            self.notebook.tab("Card Transactions"),
            corner_radius=10,
            fg_color="transparent"  # Make frame background transparent
        )
        self.neo_frame = ctk.CTkFrame(
            self.notebook.tab("NEO Transactions"),
            corner_radius=10,
            fg_color="transparent"  # Make frame background transparent
        )
        self.card_frame.pack(expand=True, fill='both', padx=15, pady=15)
        self.neo_frame.pack(expand=True, fill='both', padx=15, pady=15)
        
        # Create Treeviews
        self.setup_card_treeview()
        self.setup_neo_treeview()
        
        # Styled refresh button
        button_frame = ctk.CTkFrame(main_container, corner_radius=10)
        button_frame.pack(pady=15)
        self.refresh_btn = ctk.CTkButton(
            button_frame,
            text="↻ Refresh",
            command=self.refresh_data,
            font=ctk.CTkFont(size=FONT_SIZE)
        )
        self.refresh_btn.pack(side='left', padx=5)
        
        # Settings button
        settings_button = ctk.CTkButton(
            button_frame,
            text="⚙ Settings",
            command=self.show_settings_popup,
            font=ctk.CTkFont(size=FONT_SIZE)
        )
        settings_button.pack(side='left', padx=5)
        
        # Initialize filter variables
        self.filter_vars = {
            'amount_from': tk.StringVar(),
            'amount_to': tk.StringVar(),
            'date_from': tk.StringVar(),
            'date_to': tk.StringVar()
        }
        
        # Check if credentials are present
        settings = load_settings()  # Replaces self.load_settings()
        if not has_credentials(settings):
            self.show_settings_popup()
            self.show_message("Please enter your credentials.")
        else:
            self.refresh_data()
        
    def show_message(self, message):
        popup = ctk.CTkToplevel(self)
        popup.title("Message")
        popup.geometry("300x150")
        self.center_popup(popup)
        
        main_frame = ctk.CTkFrame(popup, corner_radius=10)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        ctk.CTkLabel(main_frame, text=message, font=ctk.CTkFont(size=FONT_SIZE)).pack(pady=20)
        
        ctk.CTkButton(main_frame, text="OK", command=popup.destroy, font=ctk.CTkFont(size=FONT_SIZE)).pack(pady=10)

    def setup_card_treeview(self):
        # Create and configure style for Treeview
        style = ttk.Style()
        style.configure('Treeview', rowheight=30)  # Increase row height
        
        # Search frame with modern layout
        search_frame = ctk.CTkFrame(self.card_frame, corner_radius=10)
        search_frame.pack(fill='x', pady=(0, 15))
        search_frame.grid_columnconfigure(1, weight=1)
        
        # Modern search bar
        search_label = ctk.CTkLabel(search_frame, text="🔍", font=ctk.CTkFont(size=FONT_SIZE))
        search_label.grid(row=0, column=0, padx=(5, 2))
        
        self.search_var = tk.StringVar()
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            height=30,  # Increase the height
            font=ctk.CTkFont(size=FONT_SIZE)
        )
        search_entry.grid(row=0, column=1, sticky='ew', padx=5)
        search_entry.bind('<KeyRelease>', lambda e: self.search_transactions())
        
        filter_button = ctk.CTkButton(
            search_frame,
            text="⚡ Filters",
            command=self.show_filter_popup,
            font=ctk.CTkFont(size=FONT_SIZE)
        )
        filter_button.grid(row=0, column=2, padx=5)
        
        # Styled Treeview
        columns = ('amount', 'vendor', 'card_ending', 'date')
        self.card_tree = ttk.Treeview(
            self.card_frame,
            columns=columns,
            show='headings'
        )
        
        # Column styling
        for col in columns:
            self.card_tree.heading(col, text=col.title())
            self.card_tree.column(col, anchor=tk.CENTER)
        
        self.card_tree.column('amount', width=100)
        self.card_tree.column('vendor', width=200)
        self.card_tree.column('card_ending', width=100)
        self.card_tree.column('date', width=150)
        
        # Modern scrollbar
        scrollbar = ttk.Scrollbar(
            self.card_frame,
            orient='vertical',
            command=self.card_tree.yview
        )
        self.card_tree.configure(yscrollcommand=scrollbar.set)
        
        self.card_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def setup_neo_treeview(self):
        # Create and configure style for Treeview
        style = ttk.Style()
        style.configure('Treeview', rowheight=30)  # Increase row height
        
        columns = ('amount', 'account', 'date')
        self.neo_tree = ttk.Treeview(self.neo_frame, columns=columns, show='headings')
        
        # Column headers
        for col in columns:
            self.neo_tree.heading(col, text=col.title())
            self.neo_tree.column(col, anchor=tk.CENTER)
        
        self.neo_tree.column('amount', width=100)
        self.neo_tree.column('account', width=150)
        self.neo_tree.column('date', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.neo_frame, orient='vertical', command=self.neo_tree.yview)
        self.neo_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack elements
        self.neo_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def refresh_data(self):
        # Clear existing items
        self.card_tree.delete(*self.card_tree.get_children())
        self.neo_tree.delete(*self.neo_tree.get_children())
        
        # Fetch new data
        card_transactions, neo_transactions = main()
        
        if not card_transactions and not neo_transactions:
            print("No transaction details found or failed to connect to email server.")
            return
        
        # Update card transactions with reversed sorting (newest first)
        for transaction in sorted(card_transactions, 
                                key=lambda x: datetime.strptime(x.get('date', '01-Jan-1970 12:00 AM'), 
                                                              '%d-%b-%Y %I:%M %p'),
                                reverse=True):
            self.card_tree.insert('', 'end', values=(
                transaction.get('amount', '0.00'),
                transaction.get('vendor', 'No vendor'),
                transaction.get('card_ending', 'Unknown'),
                transaction.get('date', 'N/A')
            ))
        
        # Update neo transactions with reversed sorting (newest first)
        for transaction in sorted(neo_transactions,
                                key=lambda x: datetime.strptime(x.get('date', '01-Jan-1970 12:00 AM'), 
                                                              '%d-%b-%Y %I:%M %p'),
                                reverse=True):
            self.neo_tree.insert('', 'end', values=(
                transaction.get('amount', '0.00'),
                transaction.get('account', 'No account'),
                transaction.get('date', 'N/A')
            ))

    def search_transactions(self):
        search_term = self.search_var.get().lower()
        
        # Show all items if search is empty
        if not search_term:
            self.refresh_data()
            return
            
        # Hide items that don't match search
        for tree in (self.card_tree, self.neo_tree):
            for item in tree.get_children():
                values = [str(v).lower() for v in tree.item(item)['values']]
                if not any(search_term in value for value in values):
                    tree.detach(item)

    def show_filter_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Filters")
        popup.geometry("400x400")
        self.center_popup(popup)

        # Create frame with padding
        main_frame = ctk.CTkFrame(popup, corner_radius=10)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)

        # Amount filter section
        amount_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        amount_frame.pack(fill='x', pady=(0, 15))
        
        for label, var in [("Amount From:", 'amount_from'), ("Amount To:", 'amount_to')]:
            frame = ctk.CTkFrame(amount_frame, corner_radius=10)
            frame.pack(fill='x', pady=5)
            ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=FONT_SIZE)).pack(side='left', padx=(0, 10))
            ctk.CTkEntry(
                frame,
                textvariable=self.filter_vars[var],
                height=30,
                font=ctk.CTkFont(size=FONT_SIZE)
            ).pack(side='left')
        
        # Date filter section
        date_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        date_frame.pack(fill='x', pady=(0, 20))
        
        for label, var in [("Date From:", 'date_from'), ("Date To:", 'date_to')]:
            frame = ctk.CTkFrame(date_frame, corner_radius=10)
            frame.pack(fill='x', pady=5)
            ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=FONT_SIZE)).pack(side='left', padx=(0, 10))
            date_entry = ctk.CTkEntry(
                frame,
                textvariable=self.filter_vars[var],
                height=30,
                font=ctk.CTkFont(size=FONT_SIZE)
            )
            date_entry.pack(side='left')
            date_button = ctk.CTkButton(
                frame,
                text="📅",
                command=lambda var=self.filter_vars[var], parent=popup: self.show_calendar(var),
                font=ctk.CTkFont(size=FONT_SIZE)
            )
            date_button.pack(side='left', padx=5)
        
        # Action buttons
        button_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        button_frame.pack(fill='x', pady=(0, 10))
        
        def apply():
            self.filter_vars['date_from'].set(self.filter_vars['date_from'].get())
            self.filter_vars['date_to'].set(self.filter_vars['date_to'].get())
            self.apply_filters()
            popup.destroy()  # Close the filters window after applying
        
        ctk.CTkButton(
            button_frame,
            text="Apply",
            command=apply,
            font=ctk.CTkFont(size=FONT_SIZE)
        ).pack(side='right', padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Reset",
            command=self.reset_filters,
            font=ctk.CTkFont(size=FONT_SIZE)
        ).pack(side='right', padx=5)

    def show_calendar(self, date_var):
        def set_date():
            selected_date = cal.selection_get()
            date_var.set(selected_date.strftime('%Y-%m-%d'))
            top.destroy()

        # Create toplevel window
        top = ctk.CTkToplevel(self)
        top.title("Select Date")
        top.geometry("300x300")
        self.center_popup(top)
        
        # Create frame for date picker
        frame = ctk.CTkFrame(top, corner_radius=10)
        frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Use tkcalendar Calendar
        cal = Calendar(frame, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(pady=20)
        
        # Confirmation button
        ctk.CTkButton(
            frame,
            text="Select",
            command=set_date,
            font=ctk.CTkFont(size=FONT_SIZE)
        ).pack(pady=10)
        
        # Remove grab_set() and wait_window() to prevent closing the filters window

    def apply_filters(self):
        self.refresh_data()  # Reset to full data
        self.filter_transactions()

    def filter_transactions(self):
        # Get filter values
        amount_from = self.filter_vars['amount_from'].get().strip()
        amount_to = self.filter_vars['amount_to'].get().strip()
        date_from = self.filter_vars['date_from'].get()
        date_to = self.filter_vars['date_to'].get()
        
        for item in self.card_tree.get_children():
            values = self.card_tree.item(item)['values']
            
            # Parse transaction amount
            try:
                amount_str = re.sub(r'[^\d\.-]', '', values[0])
                amount = float(amount_str)
            except ValueError:
                continue  # Skip items with invalid amount format
            
            # Parse filter amounts (only if they're not empty)
            amount_from_val = float(amount_from) if amount_from else float('-inf')
            amount_to_val = float(amount_to) if amount_to else float('inf')
            
            show_item = True
            
            # Inclusive range comparison
            if not (amount_from_val <= amount <= amount_to_val):
                show_item = False
                
            # Date filtering logic
            # Parse transaction date
            try:
                transaction_date = datetime.strptime(values[3], '%d-%b-%Y %I:%M %p')
            except ValueError:
                continue  # Skip items with invalid date format
            
            # Parse filter dates (only if they're not empty)
            date_from_val = datetime.strptime(date_from, '%Y-%m-%d') if date_from else datetime.min
            if date_to:
                date_to_val = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(hours=23, minutes=59, seconds=59)
            else:
                date_to_val = datetime.max
            
            # Inclusive range comparison for dates
            if not (date_from_val <= transaction_date <= date_to_val):
                show_item = False
            
            # Show or hide the item based on the filters
            if show_item:
                self.card_tree.reattach(item, '', 'end')
            else:
                self.card_tree.detach(item)

    def reset_filters(self):
        # Clear all filter variables
        for var in self.filter_vars.values():
            var.set('')
        
        # Refresh data to show all transactions
        self.refresh_data()

    def show_settings_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Settings")
        popup.geometry("400x300")
        self.center_popup(popup)
        
        main_frame = ctk.CTkFrame(popup, corner_radius=10)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        settings = load_settings()
        
        # Create fields for credentials
        fields = {
            "username": tk.StringVar(value=settings.get("username", "")),
            "password": tk.StringVar(value=settings.get("password", "")),
            "imap_server": tk.StringVar(value=settings.get("imap_server", "")),
            "imap_port": tk.StringVar(value=settings.get("imap_port", ""))
        }
        
        for idx, (label, var) in enumerate(fields.items()):
            frame = ctk.CTkFrame(main_frame, corner_radius=10)
            frame.pack(fill='x', pady=5)
            ctk.CTkLabel(frame, text=label.capitalize(), font=ctk.CTkFont(size=FONT_SIZE)).pack(side='left', padx=(0, 10))
            ctk.CTkEntry(frame, textvariable=var, height=30, font=ctk.CTkFont(size=FONT_SIZE)
            ).pack(side='left', fill='x', expand=True)
        
        def save_settings():
            new_settings = {key: var.get() for key, var in fields.items()}
            with open(SETTINGS_PATH, 'w') as file:
                json.dump(new_settings, file, indent=4)
            popup.destroy()
        
        button_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        button_frame.pack(fill='x', pady=(10, 0))
        
        ctk.CTkButton(button_frame, text="Save", command=save_settings, font=ctk.CTkFont(size=FONT_SIZE)).pack(side='right', padx=5)
        ctk.CTkButton(button_frame, text="Cancel", command=popup.destroy, font=ctk.CTkFont(size=FONT_SIZE)).pack(side='right', padx=5)

    def center_popup(self, popup):
        self.update_idletasks()
        popup.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (popup.winfo_width() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    app = TransactionViewer()
    app.mainloop()