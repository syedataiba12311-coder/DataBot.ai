import os
import re
import csv
import io
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string, send_from_directory, Response
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

# Load environment variables
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRESENTATION_DIR = os.path.join(BASE_DIR, 'presentation')
DB_FILE = os.path.join(BASE_DIR, 'data_store.db')

app = Flask(__name__, static_folder=PRESENTATION_DIR, static_url_path='')

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
OWNER_WHATSAPP_NUMBER = os.getenv('OWNER_WHATSAPP_NUMBER')

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN) else None

# Google Sheets configuration
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'service_account.json')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

# --- SQLite Local Database Engine (Fallback & Live Dashboard Sync) ---
def init_local_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            sender TEXT NOT NULL,
            type TEXT NOT NULL,
            item TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL DEFAULT 0,
            total_price REAL DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_local_db()

def get_sheet():
    """Attempt to connect to Google Sheets API if credentials exist."""
    if not os.path.exists(SERVICE_ACCOUNT_FILE) or not SPREADSHEET_ID:
        return None
    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1
        return sheet
    except Exception as e:
        print(f"[Warning] Google Sheets connection error: {e}")
        return None

def save_transaction(sender, trans_type, item, quantity, unit_price=0.0):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_price = quantity * unit_price
    
    # 1. Always save to Local SQLite DB for high-speed dashboard analytics
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transactions (timestamp, sender, type, item, quantity, unit_price, total_price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (timestamp, sender, trans_type, item, quantity, unit_price, total_price))
    conn.commit()
    conn.close()
    
    # 2. Sync to Google Sheets if configured
    sheet_synced = False
    sheet = get_sheet()
    if sheet:
        try:
            sheet.append_row([timestamp, sender, trans_type, item, quantity, unit_price, total_price])
            sheet_synced = True
        except Exception as e:
            print(f"[Error] Failed to append row to Google Sheet: {e}")
            
    return {
        "timestamp": timestamp,
        "sender": sender,
        "type": trans_type,
        "item": item,
        "quantity": quantity,
        "unit_price": unit_price,
        "total_price": total_price,
        "sheet_synced": sheet_synced
    }

def get_all_transactions():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM transactions ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def process_bot_message(incoming_msg, sender="whatsapp_user"):
    msg = incoming_msg.strip().lower()
    
    # Match "sold [qty] [item] @ [price]" or "sold [qty] [item] [price]" or "sold [qty] [item]"
    sale_match_price = re.match(r'sold\s+(\d+)\s+(.+?)(?:\s*@|\s+at|\s+price|\s+for|\s+)\s*(\d+(?:\.\d+)?)$', msg)
    sale_match_simple = re.match(r'sold\s+(\d+)\s+(.+)', msg)
    
    # Match "spent [price] [item]" or "expense [price] [item]"
    expense_match = re.match(r'(?:spent|expense|paid)\s+(\d+(?:\.\d+)?)\s+(.+)', msg)
    
    if sale_match_price and not msg.startswith("spent"):
        qty = int(sale_match_price.group(1))
        item = sale_match_price.group(2).strip()
        price = float(sale_match_price.group(3))
        res = save_transaction(sender, "Sale", item, qty, price)
        sync_str = " (Synced to Google Sheets 🟢)" if res["sheet_synced"] else ""
        total_str = f" for PKR {res['total_price']:,.2f}" if price > 0 else ""
        return f"✅ *Sale Recorded!*\nItem: {item}\nQuantity: {qty}\nPrice: PKR {price:,.2f}{total_str}{sync_str}"

    elif sale_match_simple and not msg.startswith("spent") and not msg.startswith("expense"):
        qty = int(sale_match_simple.group(1))
        item = sale_match_simple.group(2).strip()
        res = save_transaction(sender, "Sale", item, qty, 0.0)
        sync_str = " (Synced to Google Sheets 🟢)" if res["sheet_synced"] else ""
        return f"✅ *Sale Recorded!*\nItem: {item}\nQuantity: {qty}{sync_str}"

    elif expense_match:
        price = float(expense_match.group(1))
        item = expense_match.group(2).strip()
        res = save_transaction(sender, "Expense", item, 1, price)
        sync_str = " (Synced to Google Sheets 🟢)" if res["sheet_synced"] else ""
        return f"🔻 *Expense Recorded!*\nCategory: {item}\nAmount: PKR {price:,.2f}{sync_str}"

    elif msg in ["report", "summary", "stats", "today"]:
        return generate_daily_report()

    elif msg in ["stock", "inventory", "items"]:
        records = get_all_transactions()
        items = {}
        for r in records:
            if r["type"] == "Sale":
                items[r["item"]] = items.get(r["item"], 0) + r["quantity"]
        if not items:
            return "📦 *Inventory Stock*\nNo items recorded yet. Use 'Sold [qty] [item]' to start logging!"
        out = "📦 *Current Item Stock Summary*\n\n"
        for item, count in items.items():
            out += f"• {item}: {count} units sold\n"
        return out

    elif msg in ["clear", "reset"]:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM transactions')
        conn.commit()
        conn.close()
        return "🧹 *Database Cleared!* All transaction history has been reset for a clean demo."

    elif msg in ["help", "commands", "start"]:
        return (
            "🤖 *DataBot Commands Guide*\n\n"
            "1️⃣ *Log Sale*: `Sold 5 shirts` or `Sold 3 jeans @ 1500`\n"
            "2️⃣ *Log Expense*: `Spent 500 transport`\n"
            "3️⃣ *Daily Summary*: `report` or `summary`\n"
            "4️⃣ *Stock Breakdown*: `stock` or `inventory`\n"
            "5️⃣ *Clear Demo Data*: `reset`"
        )
    else:
        return (
            "👋 Welcome to *DataBot.ai*!\n\n"
            "I didn't quite catch that. Try sending:\n"
            "• `Sold 5 shirts`\n"
            "• `Sold 2 jeans @ 1200`\n"
            "• `Spent 500 transport`\n"
            "• `report` for summary\n"
            "• `help` for all commands"
        )

def generate_daily_report():
    records = get_all_transactions()
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    today_sales_count = 0
    gross_revenue = 0.0
    total_expenses = 0.0
    items_sold = {}

    for r in records:
        if r["timestamp"].startswith(today_str):
            if r["type"] == "Sale":
                qty = r["quantity"]
                today_sales_count += qty
                gross_revenue += r["total_price"]
                item = r["item"]
                items_sold[item] = items_sold.get(item, 0) + qty
            elif r["type"] == "Expense":
                total_expenses += r["total_price"]

    net_profit = gross_revenue - total_expenses

    report = f"📊 *Daily Financial Summary ({today_str})*\n"
    report += "-----------------------------------\n"
    report += f"🛍️ Total Items Sold: {today_sales_count}\n"
    report += f"💰 Gross Revenue: PKR {gross_revenue:,.2f}\n"
    report += f"💸 Total Expenses: PKR {total_expenses:,.2f}\n"
    report += f"📈 Net Profit: PKR {net_profit:,.2f}\n\n"
    
    if items_sold:
        report += "*Item Breakdown:*\n"
        for item, qty in items_sold.items():
            report += f"  • {item}: {qty} units\n"
    else:
        report += "No sales recorded yet today.\n"
        
    return report

# --- Twilio Webhook Route ---
@app.route('/bot', methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '')
    sender = request.values.get('From', 'WhatsApp User')
    
    reply_text = process_bot_message(incoming_msg, sender)
    
    resp = MessagingResponse()
    resp.message(reply_text)
    return str(resp)

# --- Web Simulator & API Endpoints for Dashboard ---
@app.route('/')
def serve_index():
    return send_from_directory(PRESENTATION_DIR, 'index.html')

@app.route('/api/message', methods=['POST'])
def api_message():
    data = request.json or {}
    message = data.get('message', '')
    sender = data.get('sender', 'Web Simulator User')
    
    if not message:
        return jsonify({"error": "Message is required"}), 400
        
    reply = process_bot_message(message, sender)
    records = get_all_transactions()
    
    return jsonify({
        "status": "success",
        "reply": reply,
        "records": records
    })

@app.route('/api/records', methods=['GET'])
def api_records():
    return jsonify({
        "status": "success",
        "records": get_all_transactions(),
        "google_sheets_connected": os.path.exists(SERVICE_ACCOUNT_FILE) and bool(SPREADSHEET_ID)
    })

@app.route('/api/stats', methods=['GET'])
def api_stats():
    records = get_all_transactions()
    sales_count = sum(r["quantity"] for r in records if r["type"] == "Sale")
    revenue = sum(r["total_price"] for r in records if r["type"] == "Sale")
    expenses = sum(r["total_price"] for r in records if r["type"] == "Expense")
    
    items_map = {}
    for r in records:
        if r["type"] == "Sale":
            items_map[r["item"]] = items_map.get(r["item"], 0) + r["quantity"]
            
    sorted_items = sorted(items_map.items(), key=lambda x: x[1], reverse=True)
    
    return jsonify({
        "status": "success",
        "total_sales_count": sales_count,
        "gross_revenue": revenue,
        "expenses": expenses,
        "net_profit": revenue - expenses,
        "top_items": sorted_items[:5],
        "total_transactions": len(records),
        "sheets_status": "Connected 🟢" if (os.path.exists(SERVICE_ACCOUNT_FILE) and SPREADSHEET_ID) else "Local SQLite Mode 🟡"
    })

@app.route('/api/seed', methods=['POST'])
def api_seed():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transactions')
    
    samples = [
        ("2026-08-30 09:15:00", "whatsapp:+923001234567", "Sale", "Cotton Shirt", 5, 1200.0, 6000.0),
        ("2026-08-30 11:30:00", "whatsapp:+923009876543", "Sale", "Denim Jeans", 2, 2500.0, 5000.0),
        ("2026-08-30 13:00:00", "whatsapp:+923001234567", "Expense", "Shipping Fee", 1, 450.0, 450.0),
        ("2026-08-30 14:45:00", "whatsapp:+923004445556", "Sale", "Leather Belt", 4, 800.0, 3200.0),
        ("2026-08-30 15:20:00", "whatsapp:+923009876543", "Sale", "Cotton Shirt", 3, 1200.0, 3600.0),
    ]
    cursor.executemany('''
        INSERT INTO transactions (timestamp, sender, type, item, quantity, unit_price, total_price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', samples)
    conn.commit()
    conn.close()
    
    return jsonify({
        "status": "success",
        "message": "Demo sample data loaded successfully!",
        "records": get_all_transactions()
    })

@app.route('/api/clear', methods=['POST'])
def api_clear():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transactions')
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Database cleared."})

@app.route('/api/export', methods=['GET'])
def api_export():
    records = get_all_transactions()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Timestamp', 'Sender', 'Type', 'Item', 'Quantity', 'Unit Price (PKR)', 'Total Price (PKR)'])
    for r in records:
        writer.writerow([r['id'], r['timestamp'], r['sender'], r['type'], r['item'], r['quantity'], r['unit_price'], r['total_price']])
        
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=WhatsApp_DataBot_Report.csv"}
    )

def send_daily_report():
    if not twilio_client or not OWNER_WHATSAPP_NUMBER or not TWILIO_WHATSAPP_NUMBER:
        print("[Scheduler] Twilio background report skipped (Missing credentials).")
        return
        
    report = generate_daily_report()
    try:
        twilio_client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=report,
            to=OWNER_WHATSAPP_NUMBER
        )
        print("[Scheduler] Daily report sent via WhatsApp.")
    except Exception as e:
        print(f"[Scheduler] Failed to send daily report: {e}")

# Scheduler for daily reports at 20:00
scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_report, 'cron', hour=20, minute=0)
scheduler.start()

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 DataBot.ai Engine Starting...")
    print("📍 Dashboard URL: http://localhost:5000")
    print("⚡ Twilio Webhook URL: http://localhost:5000/bot")
    print("=" * 60)
    app.run(port=5000, debug=True, use_reloader=False)
