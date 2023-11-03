# wsgi.py
from app import create_app

app = create_app()  # Create your Flask app instance
if __name__ == '__main__':
    app.run()
