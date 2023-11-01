from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:secret@127.0.0.1:33072/flask_db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import User, Todo

# class Todo(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     description = db.Column(db.String(200))
#     completed = db.Column(db.Boolean, default=False)
#     def __repr__(self):
#         return f"Todo: {self.title}"
# migrate = Migrate(app, db)
#
# # Wrap the command in an application context
# with app.app_context():
#     # Run the migration command
#     db.create_all()
#     migrate.upgrade()


# @app.route('/')
# def index():
#     todos = []
#     return render_template('index.html', todos=todos)
#
if __name__ == '__main__':
    app.run()
