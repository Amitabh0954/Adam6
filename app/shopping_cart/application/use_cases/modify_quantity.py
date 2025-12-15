from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shopping_cart.db'
app.config['SECRET_KEY'] = os.urandom(24)

db = SQLAlchemy(app)

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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    total_price = db.Column(db.Float, nullable=False)
    product = db.relationship('Product', backref='cart_items')

    def __repr__(self):
        return f'<CartItem {self.product.name}>'

@app.route('/modify_quantity', methods=['POST'])
def modify_quantity():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    data = request.json
    cart_item_id = data.get('cart_item_id')
    quantity = data.get('quantity')

    if not cart_item_id or quantity is None:
        return jsonify({'error': 'Cart item ID and quantity are required'}), 400

    if not isinstance(quantity, int) or quantity <= 0:
        return jsonify({'error': 'Quantity must be a positive integer'}), 400

    cart_item = CartItem.query.get(cart_item_id)
    if not cart_item or cart_item.user_id != user_id:
        return jsonify({'error': 'Cart item not found or not authorized'}), 404

    cart_item.quantity = quantity
    cart_item.total_price = cart_item.product.price * quantity
    db.session.commit()

    return jsonify({'message': 'Quantity modified successfully', 'total_price': cart_item.total_price}), 200

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)