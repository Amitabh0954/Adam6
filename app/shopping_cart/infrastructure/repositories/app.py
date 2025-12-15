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

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.json
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    if not product_id:
        return jsonify({'error': 'Product ID is required'}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    user_id = session.get('user_id')
    session_id = session.sid if not user_id else None

    if user_id:
        cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    else:
        cart_item = CartItem.query.filter_by(session_id=session_id, product_id=product_id).first()

    if cart_item:
        cart_item.quantity += quantity
    else:
        new_cart_item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity, session_id=session_id)
        db.session.add(new_cart_item)

    db.session.commit()

    return jsonify({'message': 'Product added to cart successfully'}), 200

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)