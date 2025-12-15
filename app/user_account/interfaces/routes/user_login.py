from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_account.db'
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    failed_attempts = db.Column(db.Integer, default=0)
    lock_time = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    user = User.query.filter_by(username=username).first()

    if user is None:
        return jsonify({'error': 'Invalid username or password'}), 401

    if user.failed_attempts >= 3:
        current_time = time.time()
        lock_time = float(user.lock_time) if user.lock_time else 0
        if (current_time - lock_time) < 600:  # 10 minutes lockout
            remaining_time = 600 - (current_time - lock_time)
            return jsonify({'error': f'Account locked. Try again in {int(remaining_time)} seconds'}), 403
        else:
            user.failed_attempts = 0
            user.lock_time = None
            db.session.commit()

    if not check_password_hash(user.password, password):
        user.failed_attempts += 1
        if user.failed_attempts >= 3:
            user.lock_time = str(time.time())
        db.session.commit()
        return jsonify({'error': 'Invalid username or password'}), 401

    user.failed_attempts = 0
    user.lock_time = None
    db.session.commit()

    session['user_id'] = user.id
    session.permanent = True

    return jsonify({'message': 'Login successful'}), 200

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)