from flask import render_template, redirect, url_for, flash, request, jsonify
from app.main import bp
from app.models import Transaction, User
from flask import current_app
from functools import wraps
import firebase_admin
from firebase_admin import auth
from datetime import datetime

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('token')
        if not token:
            return redirect(url_for('auth.auth'))
        try:
            decoded_token = auth.verify_id_token(token)
            request.user = User.get_by_id(decoded_token['uid'])
            return f(*args, **kwargs)
        except Exception as e:
            return redirect(url_for('auth.auth'))
    return decorated_function

@bp.route('/')
def index():
    token = request.cookies.get('token')
    if not token:
        return redirect(url_for('auth.auth'))
    
    try:
        decoded_token = auth.verify_id_token(token)
        user = User.get_by_id(decoded_token['uid'])
        
        if not user:
            return redirect(url_for('auth.auth'))
            
        transactions = Transaction.get_user_transactions(user.uid)
        expenses = [t for t in transactions if t.transaction_type == 'expense']
        incomes = [t for t in transactions if t.transaction_type == 'income']
        
        total_expenses = sum(t.amount for t in expenses)
        total_income = sum(t.amount for t in incomes)
        balance = total_income - total_expenses
        
        return render_template('dashboard.html', title='דף הבית',
                             expenses=expenses[-5:], incomes=incomes[-5:],
                             total_expenses=total_expenses,
                             total_income=total_income,
                             balance=balance)
    except Exception as e:
        print(f"Error in index route: {e}")
        return redirect(url_for('auth.auth'))

@bp.route('/expenses', methods=['GET', 'POST'])
@token_required
def expenses():
    if request.method == 'POST':
        transaction = Transaction.create(
            user_id=request.user.uid,
            amount=float(request.form['amount']),
            category=request.form['category'],
            description=request.form['description'],
            date=datetime.strptime(request.form['date'], '%Y-%m-%d').isoformat(),
            transaction_type='expense'
        )
        if transaction:
            flash('ההוצאה נוספה בהצלחה')
        else:
            flash('שגיאה בהוספת ההוצאה', 'error')
        return redirect(url_for('main.expenses'))

    transactions = Transaction.get_user_transactions(request.user.uid)
    expenses = [t for t in transactions if t.transaction_type == 'expense']
    return render_template('expenses.html', title='הוצאות', expenses=expenses)

@bp.route('/income', methods=['GET', 'POST'])
@token_required
def income():
    if request.method == 'POST':
        transaction = Transaction.create(
            user_id=request.user.uid,
            amount=float(request.form['amount']),
            category=request.form['source'],
            description=request.form.get('description', ''),
            date=datetime.strptime(request.form['date'], '%Y-%m-%d').isoformat(),
            transaction_type='income'
        )
        if transaction:
            flash('ההכנסה נוספה בהצלחה')
        else:
            flash('שגיאה בהוספת ההכנסה', 'error')
        return redirect(url_for('main.income'))

    transactions = Transaction.get_user_transactions(request.user.uid)
    incomes = [t for t in transactions if t.transaction_type == 'income']
    return render_template('income.html', title='הכנסות', incomes=incomes)

@bp.route('/report')
@token_required
def report():
    transactions = Transaction.get_user_transactions(request.user.uid)
    expenses = [t for t in transactions if t.transaction_type == 'expense']
    incomes = [t for t in transactions if t.transaction_type == 'income']
    
    # Calculate totals
    total_expenses = sum(t.amount for t in expenses)
    total_income = sum(t.amount for t in incomes)
    balance = total_income - total_expenses
    
    # Group by category
    expense_by_category = {}
    for expense in expenses:
        if expense.category not in expense_by_category:
            expense_by_category[expense.category] = 0
        expense_by_category[expense.category] += expense.amount
    
    income_by_category = {}
    for income in incomes:
        if income.category not in income_by_category:
            income_by_category[income.category] = 0
        income_by_category[income.category] += income.amount
    
    return render_template('report.html', title='דוח',
                         total_expenses=total_expenses,
                         total_income=total_income,
                         balance=balance,
                         expense_by_category=expense_by_category,
                         income_by_category=income_by_category)

@bp.route('/api/transactions/summary')
@token_required
def transactions_summary():
    try:
        transactions = Transaction.get_user_transactions(request.user.uid)
        expenses = [t for t in transactions if t.transaction_type == 'expense']
        incomes = [t for t in transactions if t.transaction_type == 'income']
        
        total_expenses = sum(t.amount for t in expenses)
        total_income = sum(t.amount for t in incomes)
        balance = total_income - total_expenses
        
        return jsonify({
            'summary': {
                'total_expenses': total_expenses,
                'total_income': total_income,
                'balance': balance
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/transactions')
@token_required
def get_transactions():
    try:
        transaction_type = request.args.get('type', 'all')
        limit = int(request.args.get('limit', 10))
        
        transactions = Transaction.get_user_transactions(request.user.uid)
        
        if transaction_type != 'all':
            transactions = [t for t in transactions if t.transaction_type == transaction_type]
        
        transactions.sort(key=lambda x: x.date, reverse=True)
        transactions = transactions[:limit]
        
        return jsonify({
            'transactions': [t.to_dict() for t in transactions]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
