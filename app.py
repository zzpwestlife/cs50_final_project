import logging

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
from helpers import login_required

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:secret@127.0.0.1:33072/flask_db'
app.config['SECRET_KEY'] = '2b1a07d8b1f3b2c8de3f6b2d5d7f8a7b'
app.secret_key = '2b1a07d8b1f3b2c8de3f6b2d5d7f8a7b'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.config['TEMPLATES_AUTO_RELOAD'] = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

from models import User, Todo
logging.basicConfig(filename='logs/app.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s')


@app.route('/')
@app.route('/todo_list')
@login_required
def todo_list():
    user_id = session["user_id"]
    if user_id is None:
        return redirect("/login")

    todos = Todo.query.all()
    return render_template('todo_list.html', todos=todos)


@app.route('/add_todo', methods=['GET', 'POST'])
@login_required
def add_todo():
    user_id = session["user_id"]
    if user_id is None:
        return redirect("/login")

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        todo = Todo(title=title, description=description)
        db.session.add(todo)
        db.session.commit()
        return redirect(url_for('todo_list'))
    return render_template('add_todo.html')


# Method for editing a to-do item
@app.route('/edit_todo/<int:todo_id>', methods=['GET', 'POST'])
@login_required
def edit_todo(todo_id):
    user_id = session["user_id"]
    if user_id is None:
        return redirect("/login")

    todo = Todo.query.get_or_404(todo_id)
    if request.method == 'POST':
        todo.title = request.form['title']
        db.session.commit()
        flash('To-Do item updated successfully!', 'success')
        return redirect(url_for('todo_list'))
    return render_template('edit_todo.html', todo=todo)


# Method for deleting a to-do item
@app.route('/delete_todo/<int:todo_id>', methods=['GET', 'POST'])
@login_required
def delete_todo(todo_id):
    user_id = session["user_id"]
    if user_id is None:
        return redirect("/login")

    todo = Todo.query.get_or_404(todo_id)
    if request.method == 'POST':
        db.session.delete(todo)
        db.session.commit()
        flash('To-Do item deleted successfully!', 'success')
        return redirect(url_for('todo_list'))
    return render_template('delete_todo.html', todo=todo)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        existing_user = User.query.filter(
            db.or_(User.username == username, User.email == email)
        ).first()

        if existing_user:
            flash('Username or email already exists. Please try a different one.', 'alert alert-danger')
            logging.warn(f"User already exists: {existing_user}")
            return render_template('register.html')

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'alert alert-success')
        # return redirect(url_for('login'))
        return render_template('login.html')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        logging.info(f"User: {user}")
        if user and user.verify_password(password):
            session["user_id"] = user.id
            return redirect('/')
        else:
            flash('Invalid email or password', 'alert alert-danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
