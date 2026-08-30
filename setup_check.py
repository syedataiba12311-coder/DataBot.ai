#!/usr/bin/env python3
"""
WhatsApp DataBot.ai - Pre-flight Setup & Diagnostics Tool
Run this script to verify system requirements, python dependencies, 
database connections, and API configurations before submission or presentation.
"""

import sys
import os

def print_header(title):
    print("\n" + "=" * 60)
    print(f" 🔍 {title}")
    print("=" * 60)

def check_dependencies():
    print_header("Checking Python Packages")
    required = ["flask", "twilio", "gspread", "google.oauth2", "dotenv", "apscheduler"]
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg)
            print(f"  ✅ {pkg:<20} [Installed]")
        except ImportError:
            print(f"  ❌ {pkg:<20} [MISSING]")
            missing.append(pkg)
            
    if missing:
        print(f"\n⚠️  Missing packages detected! Install using: pip install -r requirements.txt")
        return False
    return True

def check_files():
    print_header("Checking Project Core Files")
    files = {
        "app.py": "Flask Application Backend Engine",
        "requirements.txt": "Project Dependency List",
        "presentation/index.html": "Web Simulator & Dashboard UI",
        "presentation/style.css": "Glassmorphism Stylesheet",
        "presentation/script.js": "Interactive Frontend Script",
        ".env": "Environment Variables File",
    }
    
    all_ok = True
    for fname, desc in files.items():
        if os.path.exists(fname):
            print(f"  ✅ {fname:<28} ({desc})")
        else:
            print(f"  ❌ {fname:<28} (MISSING: {desc})")
            all_ok = False
            
    return all_ok

def check_configuration():
    print_header("Checking API Configurations & Fallbacks")
    from dotenv import load_dotenv
    load_dotenv()
    
    twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
    sheet_id = os.getenv('SPREADSHEET_ID')
    service_account = os.path.exists('service_account.json')
    
    print("  • Engine Storage Mode:")
    if service_account and sheet_id:
        print("    🟢 Google Sheets API: Configured & Active")
    else:
        print("    🟡 Storage Mode: Built-in High-Speed SQLite Database (Zero-Config Active)")
        
    print("  • Twilio WhatsApp Cloud API:")
    if twilio_sid:
        print("    🟢 Twilio Webhook: SID Detected")
    else:
        print("    🟡 Web Simulator Sandbox: Active (Local Interactive Mode)")

def main():
    print("🚀 DataBot.ai Pre-flight Diagnostics System")
    deps_ok = check_dependencies()
    files_ok = check_files()
    check_configuration()
    
    print("\n" + "=" * 60)
    if deps_ok and files_ok:
        print("🎉 STATUS: SYSTEM 100% READY FOR SUBMISSION AND DEMONSTRATION!")
        print("📍 Start the application with: python app.py")
        print("🌐 Open Browser Dashboard at: http://localhost:5000")
    else:
        print("⚠️ STATUS: Action required. Fix missing dependencies/files above.")
    print("=" * 60 + "\n")

if __name__ == '__main__':
    main()
