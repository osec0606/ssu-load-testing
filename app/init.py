from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, TestResult 
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_results.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def init_db():
    with app.app_context():
        db.drop_all()  
        db.create_all()
        print("Database initialized.")
    return app

if __name__ == "__main__":
    init_db()
