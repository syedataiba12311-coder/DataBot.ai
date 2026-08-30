# 📱 WhatsApp DataBot.ai - Complete Business Automation & Analytics System

> **Submission-Ready Project**: An AI-powered WhatsApp Business bot and interactive web dashboard that converts unstructured incoming text messages into structured financial logs, live analytics, and Google Sheets entries.

![System Overview](presentation/style.css)

---

## 🌟 Executive Summary & Key Features

**WhatsApp DataBot.ai** solves the problem of manual business record-keeping for small businesses, e-commerce stores, and service providers. Instead of requiring complex inventory apps, business owners and staff simply text sales or expense notes on WhatsApp. The bot parses the message, logs structured data to Google Sheets & a local SQLite database, and returns instant financial confirmation.

### Core Capabilities:
1. **Natural Language Regex Parsing Engine**:
   - Log sales: `Sold 5 shirts` or `Sold 3 jeans @ 2500`
   - Log expenses: `Spent 450 shipping` or `Expense 1200 electricity`
   - View inventory stock: `stock` or `inventory`
   - Get daily financial summary: `report` or `summary`
   - Reset demo dataset: `reset` or `clear`
2. **Interactive Live Web Simulator & Sandbox**:
   - Built-in live WhatsApp chat simulator allows anyone evaluating or testing the project to interact with the bot directly from their browser—with zero external API keys needed!
3. **Real-time Live Analytics & Financial Dashboard**:
   - Live KPI Metrics: **Total Sales Count**, **Gross Revenue (PKR)**, **Total Expenses**, and **Net Profit**.
   - Interactive Bar Chart breakdown of Top Selling Items (powered by Chart.js).
   - Dynamic Table view of all sales transactions with status indicators.
4. **Dual Engine Storage (Cloud + Zero-Config Standalone Fallback)**:
   - **Production Mode**: Seamlessly syncs to Google Sheets via `gspread` and accepts live WhatsApp webhooks via Twilio.
   - **Zero-Config Standalone Mode**: Uses a local SQLite database (`data_store.db`) when cloud credentials are omitted, guaranteeing that `python app.py` works 100% out of the box for evaluation.
5. **Nightly Automated Financial Reports**:
   - Built-in `APScheduler` worker sends an automated daily revenue report to the business owner every evening at 8:00 PM.
6. **One-Click CSV Export**:
   - Download complete structured transaction logs as formatted CSV files.

---

## 🚀 Quick Start Guide (Run in 1 Command)

### Prerequisites
- Python 3.8+ installed on system.

### 1. Install Dependencies & Run
Open terminal in the project directory and run:

```bash
# 1. Install required packages
pip install -r requirements.txt

# 2. Run system setup diagnostics (optional but recommended)
python setup_check.py

# 3. Start application
python app.py
```

### 2. Access Web Simulator & Dashboard
Once started, open your browser and navigate to:
👉 **[http://localhost:5000](http://localhost:5000)**

---

## 🛠️ Project Structure

```text
WhatsAppBot/
├── app.py                      # Core Flask API, Bot Parser, SQLite & Google Sheets Engine
├── requirements.txt            # Python Package Dependencies
├── setup_check.py              # Pre-flight Setup & Diagnostics Utility
├── run.bat                     # One-click Launcher for Windows
├── data_store.db               # Local SQLite Database (auto-generated)
├── service_account.json        # Google Cloud Credentials (Optional)
├── .env                        # Local Environment Variables
├── .env.example                # Environment Variable Template
├── README.md                   # Complete Submission Documentation
└── presentation/               # Interactive Web Application & Simulator
    ├── index.html              # Modern Dark Glassmorphism Frontend UI
    ├── style.css               # Responsive Layout & Animation Stylesheet
    └── script.js               # Web Audio, Live Simulator & Analytics Script
```

---

## 💬 Supported Bot Commands

| Command Example | Intent / Action | Result |
| :--- | :--- | :--- |
| `Sold 5 shirts` | Record sale without price | Logs 5 units of `shirts` with PKR 0.00 unit price |
| `Sold 2 jeans @ 2500` | Record sale with price | Logs 2 units of `jeans` at PKR 2,500 each (Total: PKR 5,000) |
| `Spent 450 transport` | Record business expense | Logs PKR 450 expense under category `transport` |
| `report` | Generate daily summary | Returns total items sold, gross revenue, expenses & net profit |
| `stock` | Item inventory check | Lists all recorded items and total sales count |
| `reset` | Clear test history | Clears database for a clean demo presentation |
| `help` | Commands menu | Displays full bot usage instructions |

---

## 🔌 API Endpoint Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the interactive Web Application & Simulator |
| `POST` | `/bot` | Twilio WhatsApp Incoming Webhook Route |
| `POST` | `/api/message` | Web Simulator chat interface endpoint |
| `GET` | `/api/records` | Returns JSON list of all transactions |
| `GET` | `/api/stats` | Returns total sales, gross revenue, expenses, net profit & top items |
| `POST` | `/api/seed` | Seeds 5 realistic sample transactions for immediate presentation |
| `POST` | `/api/clear` | Clears all recorded transaction history |
| `GET` | `/api/export` | Downloads formatted CSV financial report file |

---

## 🌐 Setting Up Live Twilio & Google Sheets (Optional Production Integration)

To connect the system to real WhatsApp numbers and live Google Sheets:

### 1. Google Sheets Credentials
1. Open [Google Cloud Console](https://console.cloud.google.com/) and create a project.
2. Enable **Google Sheets API** and **Google Drive API**.
3. Create a **Service Account**, generate a JSON key, rename it to `service_account.json`, and place it in the `WhatsAppBot/` root directory.
4. Create a Google Sheet, add header columns: `Timestamp`, `Sender`, `Type`, `Item`, `Quantity`, `Unit Price`, `Total Price`.
5. Share the Google Sheet with the Service Account email (Editor permissions).
6. Copy the Spreadsheet ID from the URL and set `SPREADSHEET_ID` in your `.env` file.

### 2. Twilio WhatsApp Setup
1. Create a [Twilio Account](https://www.twilio.com/) and navigate to Messaging Sandbox.
2. Expose your local Flask server to the internet using ngrok:
   ```bash
   ngrok http 5000
   ```
3. Set the Twilio Sandbox Webhook URL to: `https://<your-ngrok-url>/bot`
4. Send `Sold 5 shirts` from your phone to the Twilio Sandbox WhatsApp number!

---

## ✅ Submission Checklist

- [x] **Backend Logic**: Flask application with dual-engine fallback (SQLite + Google Sheets).
- [x] **Message Parser**: Flexible regex for quantities, item names, prices, expenses, and reports.
- [x] **Interactive Simulator**: Web-based WhatsApp chat sandbox with typing animation and Web Audio.
- [x] **Analytics Dashboard**: Real-time KPI metric cards, data sheet table, and Chart.js visualizations.
- [x] **CSV Data Export**: One-click download of full business reports.
- [x] **Pre-flight Diagnostics**: `setup_check.py` script for instant validation.
- [x] **Complete Documentation**: Professional README with setup instructions and architecture diagram.

---

*WhatsApp DataBot.ai • Created for Submission and Demonstration*
