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
from main import main
from gui import TransactionViewer
from datetime import datetime
from functions_gui import ensure_settings_file, load_settings, SETTINGS_PATH
import json

class FrontPage(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Front Page - Payment Overview")
        self.geometry("1000x700")

        # Scan emails once at startup
        self.card_data, self.neo_data = main()

        # Track the order of widgets
        self.front_widgets = []

        # Compute the monthly sum
        monthly_sum = 0.00
        now = datetime.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        for tx in self.card_data:
            try:
                tx_date = datetime.strptime(tx['date'], '%d-%b-%Y %I:%M %p')
                if tx_date >= start_of_month and tx_date <= now:
                    monthly_sum += float(tx['amount'].replace(',', ''))
            except:
                pass

        # Placeholder section for payment statistics
        label = ctk.CTkLabel(self, text="Payment Statistics", font=ctk.CTkFont(size=22, weight="bold"))

        # Create a frame to display the monthly sum
        monthly_sum_frame = ctk.CTkFrame(
            self,
            corner_radius=15,
            fg_color="#2F2F2F"
        )
        monthly_sum_label = ctk.CTkLabel(
            monthly_sum_frame,
            text=f"Paid this month: {monthly_sum:.2f} AED",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        monthly_sum_label.pack(padx=20, pady=20)

        chart_placeholder = ctk.CTkLabel(self, text="[ Graphs / Charts Placeholder ]", width=40, height=10)
        button = ctk.CTkButton(self, text="Transaction Details", command=self.show_transaction_viewer)
        settings_button = ctk.CTkButton(
            self,
            text="Settings",
            command=self.show_settings_popup
        )

        # Store each widget with its pack arguments
        self.front_widgets = [
            (label, {"pady": 20}),
            (
                monthly_sum_frame,
                {"side": "left", "padx": 10, "pady": 10, "anchor": "nw"}  # Position on the left
            ),
            (chart_placeholder, {"pady": 10}),
            (button, {"pady": 20}),
            (settings_button, {"pady": 20})
        ]

        # Initial packing
        for widget, pack_args in self.front_widgets:
            widget.pack(**pack_args)

    def show_transaction_viewer(self):
        # Hide all widgets on the front page
        for w, _ in self.front_widgets:
            w.pack_forget()

        # Create and pack the TransactionViewer frame passing scanned data
        self.viewer = TransactionViewer(self, self.card_data, self.neo_data)
        self.viewer.pack(fill="both", expand=True)

    def show_main_page(self):
        self.viewer.destroy()

        # Re-pack the stored widgets with the original pack arguments
        for w, pack_args in self.front_widgets:
            w.pack(**pack_args)

    def show_settings_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Settings")
        popup.geometry("400x300")
        self.center_popup(popup)

        main_frame = ctk.CTkFrame(popup, corner_radius=10)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)

        settings = load_settings()

        fields = {
            "username": tk.StringVar(value=settings.get("username", "")),
            "password": tk.StringVar(value=settings.get("password", "")),
            "imap_server": tk.StringVar(value=settings.get("imap_server", "")),
            "imap_port": tk.StringVar(value=settings.get("imap_port", ""))
        }

        for idx, (label, var) in enumerate(fields.items()):
            frame = ctk.CTkFrame(main_frame, corner_radius=10)
            frame.pack(fill='x', pady=5)
            ctk.CTkLabel(frame, text=label.capitalize(), font=ctk.CTkFont(size=17)
            ).pack(side='left', padx=(0, 10))
            ctk.CTkEntry(frame, textvariable=var, height=30, font=ctk.CTkFont(size=17)
            ).pack(side='left', fill='x', expand=True)

        def save_settings():
            new_settings = {key: var.get() for key, var in fields.items()}
            with open(SETTINGS_PATH, 'w') as file:
                json.dump(new_settings, file, indent=4)
            popup.destroy()

        button_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        button_frame.pack(fill='x', pady=(10, 0))

        ctk.CTkButton(
            button_frame, text="Save", command=save_settings, font=ctk.CTkFont(size=17)
        ).pack(side='right', padx=5)
        ctk.CTkButton(
            button_frame, text="Cancel", command=popup.destroy, font=ctk.CTkFont(size=17)
        ).pack(side='right', padx=5)

    def center_popup(self, popup):
        self.update_idletasks()
        popup.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (popup.winfo_width() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    app = FrontPage()
    app.mainloop()