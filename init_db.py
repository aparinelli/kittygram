import os
from kittygram import app, db

DATABASE_PATH = os.path.abspath(os.getcwd() + '/kittygram/database.db')

if os.path.exists(DATABASE_PATH):
    os.remove(DATABASE_PATH)

db.create_all()