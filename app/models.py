from flask_sqlalchemy import SQLAlchemy
import datetime
db = SQLAlchemy()

class TestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now) 
    details = db.Column(db.Text, nullable=False)
    message = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(255), nullable=False)


