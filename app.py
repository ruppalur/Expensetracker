import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, abort
from flask import jsonify


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

USERS = ['Ram Uppaluri', 'Sowmya Amidala']
TXNTYPES = ['Income', 'Expense']
TXNCATEGORIES = ['Salary', 'Rent', 'CreditCard', 'Utilities', 'Entertainment', 'Travel', 'Shopping', 'Miscellaneous']
SAVINGSBANKS = ['SBI','ICICIBANK','KOTAKBANK','CITIBANK']
CREDITCARDS = ['AXISBANK','HDFCBANK','PAYTM','CITIBANK','ICICIBANK','KOTAKBANK']


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_txn(txn_id):
    conn = get_db_connection()
    txn = conn.execute('SELECT * FROM account WHERE id = ?',
                        (txn_id,)).fetchone()
    conn.close()
    if txn is None:
        abort(404)
    return txn

def get_planningmonths():
    conn = get_db_connection()
    planningmonths = conn.execute('SELECT DISTINCT planningmonth FROM account').fetchall()
    conn.close()
    return planningmonths

def get_txns_frommonth(month):
    # Calculate Income Summary and Expense Summary
    summary = {}
    total_by_bank = {}
    income_summary = 0
    expense_summary = 0
    conn = get_db_connection()
    txns = conn.execute('SELECT * FROM account WHERE planningmonth = ?',
                        (month,)).fetchall()
    conn.close()
    for txn in txns:
        amount_str = txn['amount']
        try:
            amount = int(amount_str)
        except ValueError:
            # Handle the error, e.g., print an error message or set amount to a default value.
            print(f"Invalid amount value: {amount_str}")
            continue  # Skip this transaction and proceed to the next one
        if txn['txntype'] == 'Income':
            income_summary += amount
        elif txn['txntype'] == 'Expense':
            expense_summary += amount
            # Calculate total amount by bank for the month
            bank = txn['bank']
            amount = txn['amount']
            if bank in total_by_bank:
                total_by_bank[bank] += amount
            else:
                total_by_bank[bank] = amount
    # Calculate Difference between Income and Expense
    summary['income_summary'] = income_summary
    summary['expense_summary'] = expense_summary
    summary['difference'] = income_summary - expense_summary
    summary['total_by_bank'] = total_by_bank
    if txns is None:
        abort(404)
    return txns,summary


@app.route('/', methods=('GET', 'POST'))
def index():
    output = {}
    planningmonths = get_planningmonths()
    for month in planningmonths:
        output[month] = get_txns_frommonth(month['planningmonth'])
    return render_template('index.html', output=output, planningmonths=planningmonths, users=USERS, txntypes=TXNTYPES, banks=SAVINGSBANKS, creditcards=CREDITCARDS, txncategories=TXNCATEGORIES)


# create one entry 
@app.route('/createone/', methods=('GET', 'POST'))
def createone():
    if request.method == 'POST':
        user = request.form['user']
        txndate = request.form['txndate']
        txntype = request.form['txntype']
        txncategory = request.form['txncategory']
        txndescription = request.form['txndescription']
        amount = request.form['amount']
        bank = request.form['bank']
        planning_month = request.form['planning_month']

        if not user or not txndate or not txntype or not txncategory or not txndescription or not amount or not bank or not planning_month:
            return render_template('createone.html', users=user, txndates=txndate, txntypes=txntype, txncategories=txncategory, txndescriptions=txndescription, amounts=amount, banks=bank, planning_months=planning_month)
        else:
            conn = get_db_connection()
            conn.execute("INSERT INTO account (user, txndate, txntype, txncategory, txndescription, amount, bank, planningmonth) VALUES (?, ?, ?, ?, ?, ?, ?,?)",
                         (user, txndate, txntype, txncategory, txndescription, amount, bank, planning_month))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('createone.html',users=USERS, txntypes=TXNTYPES, banks=SAVINGSBANKS, creditcards=CREDITCARDS, txncategories=TXNCATEGORIES)


# create one multiple entry 
@app.route('/createmultiple/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        #print("Form Data Received:", request.form)
        #print("Request Payload:", request.get_data())
        users = request.form.getlist('user[]')
        txndates = request.form.getlist('txndate[]')
        txntypes = request.form.getlist('txntype[]')
        txncategories = request.form.getlist('txncategory[]')
        txndescriptions = request.form.getlist('txndescription[]')
        amounts = request.form.getlist('amount[]')
        banks = request.form.getlist('bank[]')
        planning_months = request.form.getlist('planningmonth[]')
        #return render_template('test.html', users=users, txndates=txndates, txntypes=txntypes, txncategories=txncategories, txndescriptions=txndescriptions, amounts=amounts, banks=banks, planning_months=planning_months)

        try:
            conn = get_db_connection()
            for i in range(len(users)):
                # Your existing code for inserting data into the database
                conn.execute("INSERT INTO account (user, txndate, txntype, txncategory, txndescription, amount, bank, planningmonth) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (users[i], txndates[i], txntypes[i], txncategories[i], txndescriptions[i], amounts[i], banks[i], planning_months[i]))
            conn.commit()
        except sqlite3.IntegrityError as e:
            print("Error inserting row", i+1, ":", e)
        except Exception as e:
            print("Error:", e)
        finally:
            conn.close()
        return redirect(url_for('index'))

    return render_template('createmultiple.html')


@app.route('/<int:id>/edit/', methods=('GET', 'POST'))
def edit(id):
    txn = get_txn(id)

    if request.method == 'POST':
        user = request.form['user']
        txndate = request.form['txndate']
        txntype = request.form['txntype']
        txncategory = request.form['txncategory']
        txndescription = request.form['txndescription']
        amount = request.form['amount']
        bank = request.form['bank']
        planning_month = request.form['planning_month']

        if not user :
            flash('All parameters are required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE account SET user = ?, txndate= ?, txntype= ?, txncategory= ?, txndescription= ?, amount= ?, bank= ?, planningmonth= ?'
                         'WHERE id=?',
                         (user, txndate, txntype, txncategory, txndescription, amount, bank, planning_month, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', txn=txn,users=USERS, txntypes=TXNTYPES, banks=SAVINGSBANKS, creditcards=CREDITCARDS, txncategories=TXNCATEGORIES)


@app.route('/<int:id>/delete/', methods=('POST',))
def delete(id):
    txn = get_txn(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM account WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(txn['id']))
    return redirect(url_for('index'))


@app.route('/<string:yearmonth>/month/', methods=('GET', 'POST'))
def edityearmonth(yearmonth):
    txns,summary = get_txns_frommonth(yearmonth)
# Calculate Income Summary and Expense Summary
    income_summary = 0
    expense_summary = 0
    for txn in txns:
        amount_str = txn['amount']
        try:
            amount = int(amount_str)
        except ValueError:
            # Handle the error, e.g., print an error message or set amount to a default value.
            print(f"Invalid amount value: {amount_str}")
            continue  # Skip this transaction and proceed to the next one

        if txn['txntype'] == 'Income':
            income_summary += amount
        elif txn['txntype'] == 'Expense':
            expense_summary += amount

    # Calculate Difference between Income and Expense
    difference = income_summary - expense_summary
    
    return render_template('index.html', txns=txns, summay=summary,  users=USERS, txntypes=TXNTYPES, banks=SAVINGSBANKS, creditcards=CREDITCARDS, txncategories=TXNCATEGORIES,planningmonths=[{'planningmonth': yearmonth }])


@app.route('/api/txns', methods=['GET'])
def get_all_txns():
    conn = get_db_connection()
    txns = conn.execute('SELECT * FROM account').fetchall()
    conn.close()
    txns_list = [dict(txn) for txn in txns]
    return jsonify(txns_list)

@app.route('/api/txns/<int:txn_id>', methods=['GET'])
def get_single_txn(txn_id):
    txn = get_txn(txn_id)
    return jsonify(dict(txn))

@app.route('/api/txns/month/<string:yearmonth>', methods=['GET'])
def get_txns_from_month(yearmonth):
    txns = get_txns_frommonth(yearmonth)
    txns_list = [dict(txn) for txn in txns]
    return jsonify(txns_list)

@app.route('/api/create', methods=['POST'])
def create_transaction():
    data = request.get_json()
    user = data.get('user')
    txndate = data.get('txndate')
    txntype = data.get('txntype')
    txncategory = data.get('txncategory')
    txndescription = data.get('txndescription')
    amount = data.get('amount')
    bank = data.get('bank')
    planning_month = data.get('planning_month')

    if not all([user, txndate, txntype, txncategory, txndescription, amount, bank, planning_month]):
        return jsonify({'error': 'All parameters are required!'}), 400

    conn = get_db_connection()
    conn.execute("INSERT INTO account (user, txndate, txntype, txncategory, txndescription, amount, bank, planningmonth) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                 (user, txndate, txntype, txncategory, txndescription, amount, bank, planning_month))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Transaction created successfully!'}), 201


@app.route('/test', methods=['GET'])
def test():
    output = {}
    planningmonths = get_planningmonths()
    for month in planningmonths:
        output[month] = get_txns_frommonth(month['planningmonth'])
    return render_template('tabsexample.html', output=output, planningmonths=planningmonths, users=USERS, txntypes=TXNTYPES, banks=SAVINGSBANKS, creditcards=CREDITCARDS, txncategories=TXNCATEGORIES)


if __name__ == "__main__":
    app.run(debug=True)