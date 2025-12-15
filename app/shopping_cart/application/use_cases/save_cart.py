from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shopping_cart.db'
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'

db = SQLAlchemy(app)
Session(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    cart_items = db.relationship('CartItem', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Product {self.name}>'

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    session_id = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<CartItem {self.product_id} - {self.quantity}>'

@app.route('/save_cart', methods=['POST'])
def save_cart():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    session_id = session.sid
    cart_items = CartItem.query.filter_by(session_id=session_id).all()

    for item in cart_items:
        item.user_id = user_id
        item.session_id = None

    db.session.commit()

    return jsonify({'message': 'Cart saved successfully'}), 200

@app.route('/load_cart', methods=['GET'])
def load_cart():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401
    
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    result = []
    for item in cart_items:
        product = Product.query.get(item.product_id)
        result.append({
            'product_id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'quantity': item.quantity
        })

    return jsonify({'cart_items': result}), 200

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True) 

