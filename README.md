# Email Transaction Scanner

A Python desktop application that fetches and displays banking transactions from email notifications using IMAP. Currently supports Mashreq Bank card transactions and NEO account notifications.

**⚠️ Work in Progress:** This project is currently under development and may undergo significant changes.

## Author's Note

Since I have opened a Mashreq bank debit card in the UAE I have been frustrated with their mobile app and online-banking website. It shows wrong transaction dates and updates them 3 days after the purchase. It is missing a lot of key features, works in just a few regions and is simply bad. I have decided to make it more convenient to manage my finances by making this app. The only way to get the transaction notifications is email or SMS (email is better imo). I use ProtonMail as my email provider of choice but use can you my app with any email you like as long as it supports IMAP.
I am planning on continuing to improve and enhance the app, so look forward for future updates.

## Features

- 🔒 Secure IMAP email connection
- 📊 Transaction filtering by date and amount
- 💳 Support for card transactions and NEO account notifications
- 🎨 Modern UI with light/dark mode support
- ⚙️ Configurable email settings
- 📅 Date range selection with calendar widget

## Prerequisites

- Python 3.8+

- ProtonMail Bridge (or any IMAP email service)

- Required Python packages:

```bash
pip install customtkinter tkcalendar
```

  

## Installation

1. Clone the repository:
```bash
git clone https://github.com/alcybersec/email-transactions-scanner
cd email-transaction-scanner
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Configure your email settings through the application's settings menu.

## Usage

1. Launch the application:
```bash
python gui.py
```
2. Configure your email settings (first time only):
    - Username
    - Password
	- IMAP Server
    - IMAP Port
3. Click "Refresh" to fetch transactions
4. Use filters to narrow down transactions by date range or amount

## Security Note

- Credentials are stored locally in ```settings.json```
- Ensure proper file permissions are set
- Consider using environment variables for sensitive data in production

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License
This project is licensed under the GNU AGPL-3.0 License - see the LICENSE file for details.
