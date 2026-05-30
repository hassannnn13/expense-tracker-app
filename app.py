from flask import Flask, redirect, render_template, request, url_for
from datetime import datetime
from models import db, Expense

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
db.init_app(app)

with app.app_context():
    if db.engine._has_events:
        db.drop_all()
    db.create_all()
    
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        title = request.form.get('title') 
        amount = request.form.get('amount')
        category = request.form.get('category')
        date_str = request.form.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.utcnow()

        new_expense = Expense(
            title=title,
            amount=float(amount),
            category=category,
            date=date
        )

        db.session.add(new_expense)
        db.session.commit()
        return redirect(url_for('home'))

    selected_category = request.args.get('category') 
    expenses_query = Expense.query 
    if selected_category:
        expenses_query = expenses_query.filter_by(category=selected_category) 

    expenses = expenses_query.all() 
    total = sum(expense.amount for expense in expenses)
    categories = [row[0] for row in db.session.query(Expense.category).distinct().order_by(Expense.category).all()] 
    return render_template('index.html', 
                           expenses=expenses, 
                           categories=categories, 
                           selected_category=selected_category, 
                           total=total
    )

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_expense(id):
    expense = db.session.get(Expense, id) 
    if not expense:
        return redirect(url_for('home'))

    if request.method == 'POST':
        title = request.form.get('title')
        amount = request.form.get('amount')
        category = request.form.get('category')
        date_str = request.form.get('date')
        expense.title = title
        expense.amount = float(amount)
        expense.category = category
        expense.date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else expense.date

        db.session.commit()
        return redirect(url_for('home'))

    return render_template('edit.html', expense=expense)

@app.route('/delete/<id>')
def delete_expense(id):
    expense = db.session.get(Expense, id)

    if expense:
        db.session.delete(expense)
        db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)

