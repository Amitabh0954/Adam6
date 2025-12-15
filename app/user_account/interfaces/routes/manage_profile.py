from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_account.db'
app.config['SECRET_KEY'] = os.urandom(24)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(80), nullable=True)
    last_name = db.Column(db.String(80), nullable=True)
    preferences = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    user_id = session['user_id']
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.json
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    preferences = data.get('preferences')
    password = data.get('password')

    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    if preferences:
        user.preferences = preferences
    if password:
        user.password = generate_password_hash(password, method='sha256')

    db.session.commit()

    return jsonify({'message': 'Profile updated successfully'}), 200

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
