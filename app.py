import logging

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
from flask_session import Session

app = Flask(__name__)
app.debug = True
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
        todo = Todo(user_id=user_id, title=title, description=description, deadline=deadline, completed=False, notified=False)
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


@app.route('/cron_send_email')
def cron_send_email():
    logging.info("cron_send_email!")
    current_time = datetime.now()
    deadline_limit = current_time + timedelta(hours=8)
    logging.info("current_time: {}".format(current_time))
    logging.info("deadline_limit: {}".format(deadline_limit))
    todos = Todo.query.filter(
        Todo.deadline <= deadline_limit,
        Todo.deadline >= current_time,
        Todo.completed == False,
        Todo.notified == False
    ).all()

    for todo in todos:
        logging.info("Sending email for todo: {}".format(todo.id))
        result = send_email(todo.id)
        if result:
            todo.notified = True
            db.session.commit()

    return "Cron job executed successfully!"


def send_email(todo_id):
    todo = Todo.query.get(todo_id)
    if todo:
        if todo.completed:
            logging.info("Todo {} is already completed!".format(todo.id))
            return True
        else:
            user = User.query.get(todo.user_id)
            if not user:
                logging.info("User {} not found!".format(todo.user_id))
                return False
    else:
        logging.info("Todo {} not found!".format(todo_id))
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
                "HTMLPart": "<h3>Dear {}, <br>"
                            "please visit <a href='http://127.0.0.1:5000'>here</a> to complete your to-do. <br><br>"
                            "Title: {} <br>"
                            "Description: {} <br>"
                            "Deadline: {} <br>"
                            " <br> May the flask force be with you!<h3>".format(
                    user.username, todo.title, todo.description, todo.deadline),
                "CustomID": str(todo.id)
            }
        ]
    }

    result = mailjet.send.create(data=data)
    logging.info("Mailjet result: {}".format(result.status_code))
    if result.status_code != 200:
        return False
    return True


if __name__ == '__main__':
    app.run()
