from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:secret@127.0.0.1:33072/flask_db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import User, Todo


@app.route('/')
def index():
    todos = Todo.query.all()
    return render_template('index.html', todos=todos)

@app.route('/add_todo', methods=['GET', 'POST'])
def add_todo():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        todo = Todo(title=title, description=description)
        db.session.add(todo)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_todo.html')

#
if __name__ == '__main__':
    app.run()
