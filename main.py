import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QPushButton, QLineEdit, QComboBox, QDateEdit, QMessageBox, QFileDialog,
    QSplitter, QGroupBox, QSizePolicy
)
from PyQt5.QtCore import QDate
from models import LedgerManager, Transaction
from autotag import auto_tag_category
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from collections import defaultdict
from utils import export_transactions_to_csv, export_ledger_to_csv
import csv

class TransactionsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.manager = LedgerManager()
        self.manager.load_from_json('data.json')
        self.editing_row = None
        self.filtered_transactions = self.manager.transactions.copy()
        self.init_ui()
        self.load_transactions()
        self.update_bar_chart()

    def init_ui(self):
        layout = QVBoxLayout()
        # Export/Import buttons
        btn_layout = QHBoxLayout()
        self.export_btn = QPushButton('Export CSV')
        self.export_btn.clicked.connect(self.export_csv)
        self.import_btn = QPushButton('Import CSV')
        self.import_btn.clicked.connect(self.import_csv)
        btn_layout.addWidget(self.export_btn)
        btn_layout.addWidget(self.import_btn)
        layout.addLayout(btn_layout)
        # Filter section
        filter_layout = QHBoxLayout()
        self.category_filter = QComboBox()
        self.category_filter.addItem('All')
        self.category_filter.addItems(sorted({t.category for t in self.manager.transactions}))
        self.date_from_filter = QDateEdit()
        self.date_from_filter.setCalendarPopup(True)
        self.date_from_filter.setDisplayFormat('yyyy-MM-dd')
        self.date_from_filter.setDate(QDate(2000, 1, 1))
        self.date_to_filter = QDateEdit(QDate.currentDate())
        self.date_to_filter.setCalendarPopup(True)
        self.date_to_filter.setDisplayFormat('yyyy-MM-dd')
        self.amount_min_filter = QLineEdit()
        self.amount_min_filter.setPlaceholderText('Min Amount')
        self.amount_max_filter = QLineEdit()
        self.amount_max_filter.setPlaceholderText('Max Amount')
        self.desc_search = QLineEdit()
        self.desc_search.setPlaceholderText('Search Description')
        self.filter_btn = QPushButton('Filter')
        self.filter_btn.clicked.connect(self.apply_filters)
        filter_layout.addWidget(QLabel('Category:'))
        filter_layout.addWidget(self.category_filter)
        filter_layout.addWidget(QLabel('Date From:'))
        filter_layout.addWidget(self.date_from_filter)
        filter_layout.addWidget(QLabel('To:'))
        filter_layout.addWidget(self.date_to_filter)
        filter_layout.addWidget(self.amount_min_filter)
        filter_layout.addWidget(self.amount_max_filter)
        filter_layout.addWidget(self.desc_search)
        filter_layout.addWidget(self.filter_btn)
        layout.addLayout(filter_layout)
        # Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(['Amount', 'Date', 'Description', 'Category', 'Type'])
        self.table.cellClicked.connect(self.on_row_selected)
        layout.addWidget(self.table)
        # Form
        form_layout = QHBoxLayout()
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText('Amount')
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText('Description')
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText('Category (auto)')
        self.type_input = QComboBox()
        self.type_input.addItems(['income', 'expense'])
        self.add_btn = QPushButton('Add')
        self.add_btn.clicked.connect(self.add_transaction)
        self.save_btn = QPushButton('Save')
        self.save_btn.clicked.connect(self.save_transaction)
        self.save_btn.setVisible(False)
        self.cancel_btn = QPushButton('Cancel')
        self.cancel_btn.clicked.connect(self.cancel_edit)
        self.cancel_btn.setVisible(False)
        self.delete_btn = QPushButton('Delete')
        self.delete_btn.clicked.connect(self.delete_transaction)
        self.desc_input.textChanged.connect(self.update_category_autotag)
        form_layout.addWidget(self.amount_input)
        form_layout.addWidget(self.date_input)
        form_layout.addWidget(self.desc_input)
        form_layout.addWidget(self.category_input)
        form_layout.addWidget(self.type_input)
        form_layout.addWidget(self.add_btn)
        form_layout.addWidget(self.save_btn)
        form_layout.addWidget(self.cancel_btn)
        form_layout.addWidget(self.delete_btn)
        layout.addLayout(form_layout)
        # Bar chart (improved)
        self.bar_canvas = FigureCanvas(Figure(figsize=(4, 2)))
        self.bar_canvas.setMaximumWidth(500)
        layout.addWidget(QLabel('Monthly Income vs Expenses (Bar Chart)'))
        layout.addWidget(self.bar_canvas)
        self.setLayout(layout)

    def update_bar_chart(self):
        self.bar_canvas.figure.clear()
        ax = self.bar_canvas.figure.add_subplot(111)
        from collections import defaultdict
        monthly_income = defaultdict(float)
        monthly_expense = defaultdict(float)
        for t in self.filtered_transactions:
            month = t.date[:7]  # yyyy-mm
            if t.trans_type == 'income':
                monthly_income[month] += t.amount
            elif t.trans_type == 'expense':
                monthly_expense[month] += t.amount
        months = sorted(set(list(monthly_income.keys()) + list(monthly_expense.keys())))
        income_vals = [monthly_income[m] for m in months]
        expense_vals = [monthly_expense[m] for m in months]
        if months:
            import numpy as np
            x = np.arange(len(months))
            width = 0.32
            gap = 0.04
            ax.bar(x - (width/2 + gap/2), income_vals, width, label='Income', color='green')
            ax.bar(x + (width/2 + gap/2), expense_vals, width, label='Expense', color='red')
            ax.set_xticks(x)
            ax.set_xticklabels(months, rotation=45, ha='right')
            ax.set_ylabel('Amount')
            ax.legend()
            ax.set_title('Monthly Income vs Expenses')
        else:
            ax.text(0.5, 0.5, 'No data', ha='center', va='center')
        self.bar_canvas.draw()

    def apply_filters(self):
        cat = self.category_filter.currentText()
        date_from = self.date_from_filter.date().toString('yyyy-MM-dd')
        date_to = self.date_to_filter.date().toString('yyyy-MM-dd')
        min_amt = self.amount_min_filter.text()
        max_amt = self.amount_max_filter.text()
        desc = self.desc_search.text().lower()
        filtered = []
        for t in self.manager.transactions:
            if cat != 'All' and t.category != cat:
                continue
            if t.date < date_from or t.date > date_to:
                continue
            if min_amt and t.amount < float(min_amt):
                continue
            if max_amt and t.amount > float(max_amt):
                continue
            if desc and desc not in t.description.lower():
                continue
            filtered.append(t)
        self.filtered_transactions = filtered
        self.load_transactions()
        self.update_bar_chart()

    def update_category_autotag(self):
        desc = self.desc_input.text()
        category = auto_tag_category(desc)
        self.category_input.setText(category)

    def add_transaction(self):
        try:
            amount = float(self.amount_input.text())
            date = self.date_input.date().toString('yyyy-MM-dd')
            desc = self.desc_input.text()
            category = self.category_input.text() or auto_tag_category(desc)
            trans_type = self.type_input.currentText()
            t = Transaction(amount, date, desc, category, trans_type)
            self.manager.add_transaction(t)
            self.manager.save_to_json('data.json')
            self.manager.load_from_json('data.json')
            self.filtered_transactions = self.manager.transactions.copy()
            self.refresh_filters()
            self.clear_form()
            self.update_bar_chart()
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Invalid input: {e}')

    def on_row_selected(self, row, column):
        t = self.filtered_transactions[row]
        self.amount_input.setText(str(t.amount))
        self.date_input.setDate(QDate.fromString(t.date, 'yyyy-MM-dd'))
        self.desc_input.setText(t.description)
        self.category_input.setText(t.category)
        self.type_input.setCurrentText(t.trans_type)
        self.editing_row = row
        self.add_btn.setVisible(False)
        self.save_btn.setVisible(True)
        self.cancel_btn.setVisible(True)

    def save_transaction(self):
        if self.editing_row is None:
            return
        try:
            amount = float(self.amount_input.text())
            date = self.date_input.date().toString('yyyy-MM-dd')
            desc = self.desc_input.text()
            category = self.category_input.text() or auto_tag_category(desc)
            trans_type = self.type_input.currentText()
            t = Transaction(amount, date, desc, category, trans_type)
            idx = self.manager.transactions.index(self.filtered_transactions[self.editing_row])
            self.manager.transactions[idx] = t
            self.manager.save_to_json('data.json')
            self.manager.load_from_json('data.json')
            self.filtered_transactions = self.manager.transactions.copy()
            self.refresh_filters()
            self.clear_form()
            self.editing_row = None
            self.add_btn.setVisible(True)
            self.save_btn.setVisible(False)
            self.cancel_btn.setVisible(False)
            self.update_bar_chart()
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Invalid input: {e}')

    def cancel_edit(self):
        self.clear_form()
        self.editing_row = None
        self.add_btn.setVisible(True)
        self.save_btn.setVisible(False)
        self.cancel_btn.setVisible(False)

    def delete_transaction(self):
        if self.editing_row is None:
            QMessageBox.warning(self, 'Error', 'Select a transaction to delete.')
            return
        idx = self.manager.transactions.index(self.filtered_transactions[self.editing_row])
        del self.manager.transactions[idx]
        self.manager.save_to_json('data.json')
        self.manager.load_from_json('data.json')
        self.filtered_transactions = self.manager.transactions.copy()
        self.refresh_filters()
        self.clear_form()
        self.editing_row = None
        self.add_btn.setVisible(True)
        self.save_btn.setVisible(False)
        self.cancel_btn.setVisible(False)
        self.update_bar_chart()

    def load_transactions(self):
        self.table.setRowCount(0)
        for t in self.filtered_transactions:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(t.amount)))
            self.table.setItem(row, 1, QTableWidgetItem(t.date))
            self.table.setItem(row, 2, QTableWidgetItem(t.description))
            self.table.setItem(row, 3, QTableWidgetItem(t.category))
            self.table.setItem(row, 4, QTableWidgetItem(t.trans_type))

    def clear_form(self):
        self.amount_input.clear()
        self.desc_input.clear()
        self.category_input.clear()
        self.date_input.setDate(QDate.currentDate())
        self.type_input.setCurrentIndex(0)

    def refresh_filters(self):
        # Update category filter dropdown
        current = self.category_filter.currentText()
        self.category_filter.clear()
        self.category_filter.addItem('All')
        self.category_filter.addItems(sorted({t.category for t in self.manager.transactions}))
        idx = self.category_filter.findText(current)
        if idx != -1:
            self.category_filter.setCurrentIndex(idx)
        self.apply_filters()

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Export Transactions to CSV', '', 'CSV Files (*.csv)')
        if path:
            try:
                export_transactions_to_csv(self.filtered_transactions, path)
                QMessageBox.information(self, 'Export', 'Transactions exported successfully!')
            except Exception as e:
                QMessageBox.warning(self, 'Export Error', str(e))

    def import_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Import Transactions from CSV', '', 'CSV Files (*.csv)')
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            t = Transaction(
                                float(row['Amount']),
                                row['Date'],
                                row['Description'],
                                row['Category'],
                                row['Type']
                            )
                            self.manager.add_transaction(t)
                        except Exception:
                            continue
                self.manager.save_to_json('data.json')
                self.manager.load_from_json('data.json')
                self.filtered_transactions = self.manager.transactions.copy()
                self.refresh_filters()
                QMessageBox.information(self, 'Import', 'Transactions imported successfully!')
            except Exception as e:
                QMessageBox.warning(self, 'Import Error', str(e))

class LedgerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.manager = LedgerManager()
        self.manager.load_from_json('data.json')
        self.editing_row = None
        self.init_ui()
        self.load_ledger()
        self.update_ledger_bar_chart()

    def init_ui(self):
        layout = QVBoxLayout()
        # Export/Import buttons
        btn_layout = QHBoxLayout()
        self.export_btn = QPushButton('Export CSV')
        self.export_btn.clicked.connect(self.export_csv)
        self.import_btn = QPushButton('Import CSV')
        self.import_btn.clicked.connect(self.import_csv)
        btn_layout.addWidget(self.export_btn)
        btn_layout.addWidget(self.import_btn)
        layout.addLayout(btn_layout)
        # Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(['Name', 'Amount', 'Description', 'Date', 'Type'])
        self.table.cellClicked.connect(self.on_row_selected)
        layout.addWidget(self.table)
        # Form
        form_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('Name')
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText('Amount')
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText('Description')
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.type_input = QComboBox()
        self.type_input.addItems(['to_give', 'to_receive'])
        self.add_btn = QPushButton('Add')
        self.add_btn.clicked.connect(self.add_entry)
        self.save_btn = QPushButton('Save')
        self.save_btn.clicked.connect(self.save_entry)
        self.save_btn.setVisible(False)
        self.cancel_btn = QPushButton('Cancel')
        self.cancel_btn.clicked.connect(self.cancel_edit)
        self.cancel_btn.setVisible(False)
        self.delete_btn = QPushButton('Delete')
        self.delete_btn.clicked.connect(self.delete_entry)
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.amount_input)
        form_layout.addWidget(self.desc_input)
        form_layout.addWidget(self.date_input)
        form_layout.addWidget(self.type_input)
        form_layout.addWidget(self.add_btn)
        form_layout.addWidget(self.save_btn)
        form_layout.addWidget(self.cancel_btn)
        form_layout.addWidget(self.delete_btn)
        layout.addLayout(form_layout)
        # Subtotals and net
        self.subtotals_label = QLabel()
        layout.addWidget(self.subtotals_label)
        # Ledger bar chart
        self.ledger_bar_canvas = FigureCanvas(Figure(figsize=(5, 2)))
        layout.addWidget(QLabel('Ledger by Person (Bar Chart)'))
        layout.addWidget(self.ledger_bar_canvas)
        self.setLayout(layout)

    def update_ledger_bar_chart(self):
        self.ledger_bar_canvas.figure.clear()
        ax = self.ledger_bar_canvas.figure.add_subplot(111)
        to_give = defaultdict(float)
        to_receive = defaultdict(float)
        for e in self.manager.ledger_entries:
            if e.entry_type == 'to_give':
                to_give[e.name] += e.amount
            elif e.entry_type == 'to_receive':
                to_receive[e.name] += e.amount
        names = sorted(set(list(to_give.keys()) + list(to_receive.keys())))
        give_vals = [to_give[n] for n in names]
        receive_vals = [to_receive[n] for n in names]
        if names:
            x = range(len(names))
            ax.bar(x, give_vals, width=0.4, label='To Give', color='red', align='center')
            ax.bar(x, receive_vals, width=0.4, label='To Receive', color='green', align='edge')
            ax.set_xticks(x)
            ax.set_xticklabels(names, rotation=45, ha='right')
            ax.set_ylabel('Amount')
            ax.legend()
        else:
            ax.text(0.5, 0.5, 'No ledger data', ha='center', va='center')
        self.ledger_bar_canvas.draw()

    def add_entry(self):
        try:
            name = self.name_input.text()
            amount = float(self.amount_input.text())
            desc = self.desc_input.text()
            date = self.date_input.date().toString('yyyy-MM-dd')
            entry_type = self.type_input.currentText()
            from models import PersonLedgerEntry
            entry = PersonLedgerEntry(name, amount, desc, date, entry_type)
            self.manager.add_ledger_entry(entry)
            self.manager.save_to_json('data.json')
            self.load_ledger()
            self.clear_form()
            self.update_ledger_bar_chart()
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Invalid input: {e}')

    def on_row_selected(self, row, column):
        entry = self.manager.ledger_entries[row]
        self.name_input.setText(entry.name)
        self.amount_input.setText(str(entry.amount))
        self.desc_input.setText(entry.description)
        self.date_input.setDate(QDate.fromString(entry.date, 'yyyy-MM-dd'))
        self.type_input.setCurrentText(entry.entry_type)
        self.editing_row = row
        self.add_btn.setVisible(False)
        self.save_btn.setVisible(True)
        self.cancel_btn.setVisible(True)

    def save_entry(self):
        if self.editing_row is None:
            return
        try:
            name = self.name_input.text()
            amount = float(self.amount_input.text())
            desc = self.desc_input.text()
            date = self.date_input.date().toString('yyyy-MM-dd')
            entry_type = self.type_input.currentText()
            from models import PersonLedgerEntry
            entry = PersonLedgerEntry(name, amount, desc, date, entry_type)
            self.manager.ledger_entries[self.editing_row] = entry
            self.manager.save_to_json('data.json')
            self.load_ledger()
            self.clear_form()
            self.editing_row = None
            self.add_btn.setVisible(True)
            self.save_btn.setVisible(False)
            self.cancel_btn.setVisible(False)
            self.update_ledger_bar_chart()
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Invalid input: {e}')

    def cancel_edit(self):
        self.clear_form()
        self.editing_row = None
        self.add_btn.setVisible(True)
        self.save_btn.setVisible(False)
        self.cancel_btn.setVisible(False)

    def delete_entry(self):
        if self.editing_row is None:
            QMessageBox.warning(self, 'Error', 'Select an entry to delete.')
            return
        del self.manager.ledger_entries[self.editing_row]
        self.manager.save_to_json('data.json')
        self.load_ledger()
        self.clear_form()
        self.editing_row = None
        self.add_btn.setVisible(True)
        self.save_btn.setVisible(False)
        self.cancel_btn.setVisible(False)
        self.update_ledger_bar_chart()

    def load_ledger(self):
        self.table.setRowCount(0)
        for entry in self.manager.ledger_entries:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(entry.name))
            self.table.setItem(row, 1, QTableWidgetItem(str(entry.amount)))
            self.table.setItem(row, 2, QTableWidgetItem(entry.description))
            self.table.setItem(row, 3, QTableWidgetItem(entry.date))
            self.table.setItem(row, 4, QTableWidgetItem(entry.entry_type))
        # Subtotals
        total_to_give = sum(e.amount for e in self.manager.ledger_entries if e.entry_type == 'to_give')
        total_to_receive = sum(e.amount for e in self.manager.ledger_entries if e.entry_type == 'to_receive')
        net = total_to_receive - total_to_give
        self.subtotals_label.setText(f'Total To Give: {total_to_give} | Total To Receive: {total_to_receive} | Net Balance: {net}')
        self.update_ledger_bar_chart()

    def clear_form(self):
        self.name_input.clear()
        self.amount_input.clear()
        self.desc_input.clear()
        self.date_input.setDate(QDate.currentDate())
        self.type_input.setCurrentIndex(0)

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Export Ledger to CSV', '', 'CSV Files (*.csv)')
        if path:
            try:
                export_ledger_to_csv(self.manager.ledger_entries, path)
                QMessageBox.information(self, 'Export', 'Ledger exported successfully!')
            except Exception as e:
                QMessageBox.warning(self, 'Export Error', str(e))

    def import_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Import Ledger from CSV', '', 'CSV Files (*.csv)')
        if path:
            try:
                from models import PersonLedgerEntry
                with open(path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            entry = PersonLedgerEntry(
                                row['Name'],
                                float(row['Amount']),
                                row['Description'],
                                row['Date'],
                                row['Type']
                            )
                            self.manager.add_ledger_entry(entry)
                        except Exception:
                            continue
                self.manager.save_to_json('data.json')
                self.manager.load_from_json('data.json')
                self.load_ledger()
                QMessageBox.information(self, 'Import', 'Ledger imported successfully!')
            except Exception as e:
                QMessageBox.warning(self, 'Import Error', str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Budget Management System')
        self.setGeometry(100, 100, 900, 600)
        self.tabs = QTabWidget()
        self.tabs.addTab(TransactionsTab(), 'Transactions')
        self.tabs.addTab(LedgerTab(), 'Ledger')
        self.setCentralWidget(self.tabs)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 