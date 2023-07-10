import sqlite3
import random
from datetime import datetime, timedelta

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()


# populate dummy data

# List of available options for user, txntype, txncategory, and bank
users = ['Ram', 'Sowmya']
txn_types = ['Income', 'Expense']
income_categories = ['Salary', 'Trading']
expense_categories = ['CrCard', 'Rent', 'SupportParents', 'Miscellaneous']
banks = ['icicbank', 'Citibank', 'SBI', 'HDFC']
planning_month = '2023-01'

# Function to generate a random date within a given range
def random_date(start_date, end_date):
    days = (end_date - start_date).days
    random_days = random.randint(0, days)
    return start_date + timedelta(days=random_days)


# Generate and insert 10 rows of data into the 'account' table
for _ in range(10):
    user = random.choice(users)
    txndate = random_date(datetime(2023, 1, 1), datetime(2023, 12, 31)).strftime('%Y-%m-%d')
    txntype = random.choice(txn_types)
    if txntype == 'Income':
        txncategory = random.choice(income_categories)
    else:
        txncategory = random.choice(expense_categories)
    txndescription = f'{txncategory} transaction'
    amount = random.randint(10000, 50000)
    bank = random.choice(banks)
    print(user, txndate, txntype, txncategory, txndescription, amount, bank, planning_month)

    cur.execute("INSERT INTO account (user, txndate, txntype, txncategory, txndescription, amount, bank, planningmonth) VALUES (?, ?, ?, ?, ?, ?, ?,?)",
                (user, txndate, txntype, txncategory, txndescription, amount, bank, planning_month))


connection.commit()
connection.close()


