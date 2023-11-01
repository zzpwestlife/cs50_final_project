from app import app, db
from models import User, Todo


def seed_user():
    with app.app_context():
        # Create example users
        user1 = User(username="user1", email="user1@example.com")
        user2 = User(username="user2", email="user2@example.com")
        # Add the users to the session
        db.session.add(user1)
        db.session.add(user2)
        # Commit the changes to the database
        db.session.commit()


def seed_todo():
    with app.app_context():
        todo1 = Todo(title="Clean bedroom", description="Clean the bedroom", completed=False)
        todo2 = Todo(title="Clean bathroom", description="Clean the bathroom", completed=False)
        db.session.add(todo1)
        db.session.add(todo2)
        db.session.commit()


# Call the seed function to insert the records
seed_user()
seed_todo()
