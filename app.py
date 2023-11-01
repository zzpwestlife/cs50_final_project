from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:secret@127.0.0.1:33072/flask_db'
app.config['SECRET_KEY'] = '2b1a07d8b1f3b2c8de3f6b2d5d7f8a7b'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import User, Todo


@app.route('/')
@app.route('/todo_list')
def todo_list():
    todos = Todo.query.all()
    return render_template('todo_list.html', todos=todos)


@app.route('/add_todo', methods=['GET', 'POST'])
def add_todo():
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
def edit_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if request.method == 'POST':
        todo.title = request.form['title']
        db.session.commit()
        flash('To-Do item updated successfully!', 'success')
        return redirect(url_for('todo_list'))
    return render_template('edit_todo.html', todo=todo)


# Method for deleting a to-do item
@app.route('/delete_todo/<int:todo_id>', methods=['GET', 'POST'])
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if request.method == 'POST':
        db.session.delete(todo)
        db.session.commit()
        flash('To-Do item deleted successfully!', 'success')
        return redirect(url_for('todo_list'))
    return render_template('delete_todo.html', todo=todo)


if __name__ == '__main__':
    app.run(debug=True)
