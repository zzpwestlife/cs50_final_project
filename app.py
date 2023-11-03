import logging

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import null
from datetime import datetime

from flask_session import Session

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:secret@127.0.0.1:33072/flask_db'
app.config['SECRET_KEY'] = '2b1a07d8b1f3b2c8de3f6b2d5d7f8a7b'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.config['TEMPLATES_AUTO_RELOAD'] = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

from models import User, Todo
from helpers import login_required

from mailjet_rest import Client
import os

api_key = '25c155cab4f2ba7978a230600293dda8'
api_secret = 'a1a7dc7d1c53aaa201797f8c3570d97b'
mailjet = Client(auth=(api_key, api_secret), version='v3.1')


# logging.basicConfig(filename='logs/app.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')


@app.route('/')
@app.route('/todo_list')
@login_required
def todo_list():
    user_id = session["user_id"]
    todos = Todo.query.filter_by(user_id=user_id, completed=0).filter(Todo.deleted_at.is_(None)).all()
    return render_template('todo_list.html', todos=todos)


@app.route('/add_todo', methods=['GET', 'POST'])
@login_required
def add_todo():
    user_id = session["user_id"]
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        deadline = request.form.get('deadline')
        todo = Todo(user_id=user_id, title=title, description=description, deadline=deadline)
        db.session.add(todo)
        db.session.commit()
        return redirect(url_for('todo_list'))
    return render_template('add_todo.html')


@app.route('/edit_todo/<int:todo_id>', methods=['GET', 'POST'])
@login_required
def edit_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if request.method == 'POST':
        todo.title = request.form['title']
        todo.description = request.form['description']
        todo.deadline = request.form['deadline']
        db.session.commit()
        flash('To-Do item updated successfully!', 'alert alert-success')
        return redirect(url_for('todo_list'))
    return render_template('edit_todo.html', todo=todo)


@app.route('/delete_todo/<int:todo_id>', methods=['GET', 'POST'])
@login_required
def delete_todo(todo_id):
    user_id = session["user_id"]
    todo = Todo.query.get_or_404(todo_id)
    if todo.user_id != user_id:
        flash('You are not authorized to delete this to-do item!', 'alert alert-danger')
        return redirect(url_for('todo_list'))

    if request.method == 'POST':
        db.session.delete(todo)
        db.session.commit()
        flash('To-Do item deleted successfully!', 'alert alert-success')
        return redirect(url_for('todo_list'))
    return render_template('delete_todo.html', todo=todo)


@app.route('/complete_todo/<int:todo_id>', methods=['POST'])
def complete_todo(todo_id):
    user_id = session["user_id"]
    todo = Todo.query.get(todo_id)
    if todo:
        if todo.user_id != user_id:
            flash('You are not authorized to complete this to-do item!', 'alert alert-danger')
            return redirect(url_for('todo_list'))

        if not todo.completed:
            todo.completed = True
            db.session.commit()
            flash('To-do item marked as completed!', 'alert alert-success')
        else:
            flash('To-do item is already completed!', 'alert alert-info')
    else:
        flash('To-do item not found!', 'alert alert-danger')
    return redirect(url_for('todo_list'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    session.clear()

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        existing_user = User.query.filter(
            db.or_(User.username == username, User.email == email)
        ).first()

        if existing_user:
            flash('Username or email already exists. Please try a different one.', 'alert alert-danger')
            return render_template('register.html')

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'alert alert-success')
        return render_template('login.html')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.verify_password(password):
            session["user_id"] = user.id
            return redirect('/')
        else:
            flash('Invalid username or password', 'alert alert-danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect('/login')


def send_email(todo_id):
    todo = Todo.query.get(todo_id)
    if todo:
        if todo.completed:
            return True
        else:
            user = User.query.get(todo.user_id)
            if not user:
                return False
    else:
        return False

    data = {
        'Messages': [
            {
                "From": {
                    "Email": "zzpwestlife@gmail.com",
                    "Name": "Joey"
                },
                "To": [
                    {
                        "Email": user.email,
                        "Name": user.username,
                    }
                ],
                "Subject": "Complete your to-do item now!",
                "TextPart": "You have set the deadline for this item",
                "HTMLPart": "<h3>Dear {}, please visit <a href='http://127.0.0.1:5000/edit_todo/{}'>here</a> to complete your to-do. <br> May the flask force be with you!<h3>".format(
                    user.username, todo.id),
                "CustomID": str(todo.id)
            }
        ]
    }

    result = mailjet.send.create(data=data)
    print(result.status_code)
    print(result.json())
    return redirect('/todo_list')


if __name__ == '__main__':
    app.run(debug=True)
