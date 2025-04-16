import sys
import os

# Add your project directory to the path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

# Import the app object from your main app file
from app import app as application

# Initialize the database if needed
from app import init_db
init_db()

# For local development with uwsgi
if __name__ == "__main__":
    application.run() 