from flask import render_template, redirect, url_for, flash, request
from app.main import bp
from app.models import Expense, Income
from app import db
from flask_login import login_required, current_user
from datetime import datetime

@bp.route('/')
def index():
    if not current_user.is_authenticated:
        return render_template('index.html', title='ברוכים הבאים')
    
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).limit(5).all()
    incomes = Income.query.filter_by(user_id=current_user.id).order_by(Income.date.desc()).limit(5).all()
    
    total_expenses = db.session.query(db.func.sum(Expense.amount)).filter_by(user_id=current_user.id).scalar() or 0
    total_income = db.session.query(db.func.sum(Income.amount)).filter_by(user_id=current_user.id).scalar() or 0
    balance = total_income - total_expenses
    
    return render_template('index.html', title='דף הבית',
                         expenses=expenses, incomes=incomes,
                         total_expenses=total_expenses,
                         total_income=total_income,
                         balance=balance)

@bp.route('/expenses', methods=['GET', 'POST'])
@login_required
def expenses():
    if request.method == 'POST':
        expense = Expense(
            amount=float(request.form['amount']),
            category=request.form['category'],
            description=request.form['description'],
            date=datetime.strptime(request.form['date'], '%Y-%m-%d'),
            user_id=current_user.id
        )
        db.session.add(expense)
        db.session.commit()
        flash('ההוצאה נוספה בהצלחה')
        return redirect(url_for('main.expenses'))

    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    return render_template('expenses.html', title='הוצאות', expenses=expenses)

@bp.route('/income', methods=['GET', 'POST'])
@login_required
def income():
    if request.method == 'POST':
        income = Income(
            amount=float(request.form['amount']),
            source=request.form['source'],
            description=request.form['description'],
            date=datetime.strptime(request.form['date'], '%Y-%m-%d'),
            user_id=current_user.id
        )
        db.session.add(income)
        db.session.commit()
        flash('ההכנסה נוספה בהצלחה')
        return redirect(url_for('main.income'))

    incomes = Income.query.filter_by(user_id=current_user.id).order_by(Income.date.desc()).all()
    return render_template('income.html', title='הכנסות', incomes=incomes)

@bp.route('/report')
@login_required
def report():
    # Get date filters from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Base query with user filter
    expenses_query = Expense.query.filter_by(user_id=current_user.id)
    incomes_query = Income.query.filter_by(user_id=current_user.id)
    
    # Apply date filters if provided
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        expenses_query = expenses_query.filter(Expense.date >= start_date)
        incomes_query = incomes_query.filter(Income.date >= start_date)
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        expenses_query = expenses_query.filter(Expense.date <= end_date)
        incomes_query = incomes_query.filter(Income.date <= end_date)
    
    # Execute queries
    expenses = expenses_query.all()
    incomes = incomes_query.all()
    
    # Calculate totals
    total_expenses = sum(expense.amount for expense in expenses)
    total_income = sum(income.amount for income in incomes)
    balance = total_income - total_expenses
    
    # Group expenses by category
    expenses_by_category = {}
    for expense in expenses:
        if expense.category in expenses_by_category:
            expenses_by_category[expense.category] += expense.amount
        else:
            expenses_by_category[expense.category] = expense.amount
    
    # Group expenses and incomes by month for trend analysis
    expenses_by_month = {}
    incomes_by_month = {}
    
    for expense in expenses:
        month_key = expense.date.strftime('%Y-%m')
        if month_key in expenses_by_month:
            expenses_by_month[month_key] += expense.amount
        else:
            expenses_by_month[month_key] = expense.amount
            
    for income in incomes:
        month_key = income.date.strftime('%Y-%m')
        if month_key in incomes_by_month:
            incomes_by_month[month_key] += income.amount
        else:
            incomes_by_month[month_key] = income.amount
    
    # Calculate monthly averages
    avg_monthly_expense = total_expenses / len(expenses_by_month) if expenses_by_month else 0
    avg_monthly_income = total_income / len(incomes_by_month) if incomes_by_month else 0
    
    return render_template('report.html', 
                         title='דוחות',
                         expenses=expenses,
                         incomes=incomes,
                         total_expenses=total_expenses,
                         total_income=total_income,
                         balance=balance,
                         expenses_by_category=expenses_by_category,
                         expenses_by_month=expenses_by_month,
                         incomes_by_month=incomes_by_month,
                         avg_monthly_expense=avg_monthly_expense,
                         avg_monthly_income=avg_monthly_income,
                         start_date=start_date.strftime('%Y-%m-%d') if start_date else '',
                         end_date=end_date.strftime('%Y-%m-%d') if end_date else '')
