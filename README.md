# Budget Management System

A modern desktop application for tracking your budget, income, expenses, and personal ledgers. Built with Python and PyQt5, this tool helps you manage your finances, visualize spending, and keep track of money owed to and from individuals.

---

## Project Structure

```
BudgetManagementSystem/
├── main.py                # Main application entry point (UI and logic)
├── models.py              # Data models for transactions and ledger entries
├── autotag.py             # Auto-tagging logic for transaction categories
├── utils.py               # Utility functions (CSV export, etc)
├── requirements.txt       # Python dependencies
├── data.json              # Local data storage (auto-created)
└── README.md              # Project documentation
```

---

## Features & Functionality

### 1. Income & Expense Tracker
- **Add, edit, and delete transactions** with amount, date, description, category, and type (income/expense).
- **Auto-tagging:** Categories are suggested automatically based on keywords in the description (e.g., "uber" → Transport).
- **Table view:** All transactions are displayed in a sortable, filterable table.

### 2. To Give / To Receive Ledger
- **Track people you owe money to and those who owe you.**
- **Add, edit, and delete ledger entries** (name, amount, description, date, type).
- **Subtotals per person** and grand totals for all entries.
- **Ledger bar chart:** Visualizes balances per person (to give/to receive).

### 3. Filters & Search
- **Filter transactions** by category, date range, amount range, and description.
- **Instantly update** the table and charts based on filters.

### 4. Chart Visualizations
- **Bar chart:** Monthly income vs. expenses, with clear grouping and gaps for readability.
- **Ledger bar chart:** Shows how much you owe or are owed by each person.

### 5. CSV Import & Export
- **Export transactions and ledger** to CSV files (with headers and totals).
- **Import transactions and ledger** from CSV files for easy migration or backup.

---

## Technologies Used
- Python 3
- PyQt5 (GUI)
- Matplotlib (Charts)
- JSON (Data storage)

---

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/impranzal/budget-management-system.git
   cd budget-management-system
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *If you don't have a requirements.txt, install manually:*
   ```bash
   pip install pyqt5 matplotlib
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

---

## Usage
- Use the **Transactions** tab to add and manage your income and expenses.
- Use the **Ledger** tab to track money you owe or are owed by individuals.
- Filter, search, and visualize your data with built-in charts.
- Export or import your data as CSV for backup or migration.

---

## Author
**Pranjal Rimal**

---

## License
This project is open source and available under the MIT License. 