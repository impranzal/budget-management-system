import csv
from typing import List
from models import Transaction, PersonLedgerEntry

def export_transactions_to_csv(transactions: List[Transaction], file_path: str):
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Amount', 'Date', 'Description', 'Category', 'Type'])
        for t in transactions:
            writer.writerow([t.amount, t.date, t.description, t.category, t.trans_type])
        total_income = sum(t.amount for t in transactions if t.trans_type == 'income')
        total_expense = sum(t.amount for t in transactions if t.trans_type == 'expense')
        net = total_income - total_expense
        writer.writerow([])
        writer.writerow(['Total Income', total_income])
        writer.writerow(['Total Expense', total_expense])
        writer.writerow(['Net Balance', net])

def export_ledger_to_csv(entries: List[PersonLedgerEntry], file_path: str):
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Name', 'Amount', 'Description', 'Date', 'Type'])
        for e in entries:
            writer.writerow([e.name, e.amount, e.description, e.date, e.entry_type])
        writer.writerow([])
        total_to_give = sum(e.amount for e in entries if e.entry_type == 'to_give')
        total_to_receive = sum(e.amount for e in entries if e.entry_type == 'to_receive')
        net = total_to_receive - total_to_give
        writer.writerow(['Total To Give', total_to_give])
        writer.writerow(['Total To Receive', total_to_receive])
        writer.writerow(['Net Balance', net]) 