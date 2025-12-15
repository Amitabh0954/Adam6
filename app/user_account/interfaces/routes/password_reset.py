from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import uuid
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_account.db'
app.config['SECRET_KEY'] = os.urandom(24)
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'your-email@example.com'
app.config['MAIL_PASSWORD'] = 'your-email-password'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class PasswordReset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(200), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)

@app.route('/request_password_reset', methods=['POST'])
def request_password_reset():
    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User with this email not found'}), 404

    token = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(hours=24)
    password_reset = PasswordReset(user_id=user.id, token=token, expires_at=expires_at)
    db.session.add(password_reset)
    db.session.commit()

    reset_link = f'http://localhost:5000/reset_password/{token}'
    msg = Message('Password Reset Request', sender='noreply@example.com', recipients=[email])
    msg.body = f'To reset your password, click the following link: {reset_link}

This link will expire in 24 hours.'
    mail.send(msg)

    return jsonify({'message': 'Password reset link sent to your email'}), 200

@app.route('/reset_password/<token>', methods=['POST'])
def reset_password(token):
    data = request.json
    new_password = data.get('new_password')

    if not new_password:
        return jsonify({'error': 'New password is required'}), 400

    password_reset = PasswordReset.query.filter_by(token=token).first()
    if not password_reset or password_reset.expires_at < datetime.utcnow():
        return jsonify({'error': 'Invalid or expired token'}), 400

    user = User.query.get(password_reset.user_id)
    user.password = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({'message': 'Password has been reset successfully'}), 200

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)