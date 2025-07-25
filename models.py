from typing import List, Dict, Optional
from datetime import date
import json

class Transaction:
    def __init__(self, amount: float, date: str, description: str, category: str, trans_type: str):
        self.amount = amount
        self.date = date  # ISO format string
        self.description = description
        self.category = category
        self.trans_type = trans_type  # 'income' or 'expense'

    def to_dict(self) -> Dict:
        return {
            'amount': self.amount,
            'date': self.date,
            'description': self.description,
            'category': self.category,
            'trans_type': self.trans_type
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Transaction':
        return Transaction(
            amount=data['amount'],
            date=data['date'],
            description=data['description'],
            category=data['category'],
            trans_type=data['trans_type']
        )

class PersonLedgerEntry:
    def __init__(self, name: str, amount: float, description: str, date: str, entry_type: str):
        self.name = name
        self.amount = amount
        self.description = description
        self.date = date  # ISO format string
        self.entry_type = entry_type  # 'to_give' or 'to_receive'

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'amount': self.amount,
            'description': self.description,
            'date': self.date,
            'entry_type': self.entry_type
        }

    @staticmethod
    def from_dict(data: Dict) -> 'PersonLedgerEntry':
        return PersonLedgerEntry(
            name=data['name'],
            amount=data['amount'],
            description=data['description'],
            date=data['date'],
            entry_type=data['entry_type']
        )

class LedgerManager:
    def __init__(self):
        self.transactions: List[Transaction] = []
        self.ledger_entries: List[PersonLedgerEntry] = []

    def add_transaction(self, transaction: Transaction):
        self.transactions.append(transaction)

    def add_ledger_entry(self, entry: PersonLedgerEntry):
        self.ledger_entries.append(entry)

    def save_to_json(self, file_path: str):
        data = {
            'transactions': [t.to_dict() for t in self.transactions],
            'ledger_entries': [e.to_dict() for e in self.ledger_entries]
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def load_from_json(self, file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.transactions = [Transaction.from_dict(t) for t in data.get('transactions', [])]
            self.ledger_entries = [PersonLedgerEntry.from_dict(e) for e in data.get('ledger_entries', [])]
        except FileNotFoundError:
            self.transactions = []
            self.ledger_entries = [] 