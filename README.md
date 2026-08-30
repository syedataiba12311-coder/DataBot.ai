# 🤖 DataBot.ai — WhatsApp Business Automation System

> **Turn everyday WhatsApp messages into structured business records, financial insights, and automated reports.**

DataBot.ai is a WhatsApp-based business automation system designed for small and medium-sized businesses that still rely on manual data entry and unstructured WhatsApp conversations.

Github Repo:https://github.com/syedataiba12311-coder/DataBot.ai.git
Live URL:https://syedataiba12311-coder.github.io/DataBot.ai/
The system converts simple natural-language business messages such as:

- `Sold 5 cotton shirts`
- `Sold 2 denim jeans @ 2500`
- `Spent 450 shipping`
- `Report`

into structured business records, synchronized data, financial summaries, CSV exports, and automated reports.

---

## 🚀 Overview

Small businesses often record sales, expenses, and inventory information through WhatsApp conversations, notebooks, or manually maintained spreadsheets.

This creates several problems:

- ❌ Manual data entry
- ❌ Unstructured business information
- ❌ Human calculation errors
- ❌ Difficult financial tracking
- ❌ No centralized records
- ❌ Time-consuming reporting

**DataBot.ai solves this by acting as a business assistant directly through WhatsApp.**

A business owner simply sends a message, and the system:

```text
WhatsApp Message
       ↓
Message Parser
       ↓
Command Detection
       ↓
Data Validation
       ↓
Business Logic
✨ Key Features
💬 WhatsApp Business Assistant

Business owners can interact with DataBot.ai using simple text commands.

Example
Sold 5 Cotton Shirts

The system automatically identifies:

Transaction Type: Sale
Item: Cotton Shirts
Quantity: 5

Another example:

Sold 2 Denim Jeans @ 2500

is converted into:

Transaction Type: Sale
Item: Denim Jeans
Quantity: 2
Unit Price: PKR 2,500
Total: PKR 5,000
🧠 Smart Message Parser

DataBot.ai uses a lightweight intelligent parsing layer to understand common business messages without requiring users to follow complicated forms.

The parser can recognize patterns for:

Sales
Expenses
Products
Quantities
Prices
Reports
Help commands

Example:

Sold 10 shirts @ 1500

becomes structured transaction data.

📊 Real-Time Business Analytics

The dashboard provides an overview of business activity including:

Total sales
Total expenses
Transaction history
Product activity
Revenue trends
Business summaries

This allows business owners to understand their operations without manually calculating spreadsheet values.

📑 Google Sheets Integration

Transactions can be synchronized with Google Sheets.

This provides businesses with:

Centralized records
Easy access to transaction history
Spreadsheet-based analysis
Familiar data management
Backup and portability

The system combines a local SQLite database with Google Sheets for a dual-storage approach.

                 ┌─────────────────┐
                 │   DataBot.ai    │
                 └────────┬────────┘
                          │
              ┌───────────┴───────────┐
              ↓                       ↓
       ┌─────────────┐         ┌─────────────┐
       │   SQLite    │         │Google Sheets│
       │  Database   │         │    Sync     │
       └─────────────┘         └─────────────┘
🗄️ SQLite Database

SQLite provides a lightweight local database for storing structured business transactions.

Typical transaction information includes:

Field	Description
ID	Unique transaction identifier
Timestamp	Date and time
Phone Number	WhatsApp sender
Type	Sale / Expense
Item	Product or expense description
Quantity	Quantity involved
Unit Price	Price per item
Total	Calculated transaction value
📈 Business Reports

Users can request a summary directly through WhatsApp.

Example:

report

The system can generate a business summary based on recorded transactions.

This eliminates the need to manually calculate:

Revenue
Expenses
Transaction totals
Product sales
Business activity
📥 CSV Export

DataBot.ai supports exporting transaction records into CSV format.

This makes it easy to:

Download business data
Import data into Excel
Analyze transactions
Create custom reports
Maintain audit records
🧾 Audit Logs

Transaction activity can be maintained as structured records for traceability.

This provides businesses with a history of:

Incoming messages
Recorded transactions
Transaction timestamps
Sender information
Business actions
⏰ Automated Reports

The system is designed to support scheduled business reporting.

For example, a business can receive automated reports containing:

Daily Sales
Daily Expenses
Net Activity
Top Products
Transaction Count

This reduces the need for business owners to manually check their records every day.
       ↓
SQLite Database
       ↓
Google Sheets Sync
       ↓
Analytics / Reports / CSV
