from flask import Flask, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shopping_cart.db'
app.config['SECRET_KEY'] = os.urandom(24)

db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Product {self.name}>'

class ShoppingCartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    product = db.relationship('Product')

    def __repr__(self):
        return f'<ShoppingCartItem {self.product.name}>'

@app.route('/remove_from_cart', methods=['DELETE'])
def remove_from_cart():
    data = request.json
    product_id = data.get('product_id')
    user_id = session.get('user_id')
    confirm = data.get('confirm')

    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    if not confirm:
        return jsonify({'error': 'Confirmation is required to remove item'}), 400

    cart_item = ShoppingCartItem.query.filter_by(product_id=product_id, user_id=user_id).first()
    if not cart_item:
        return jsonify({'error': 'Product not found in cart'}), 404

    db.session.delete(cart_item)
    db.session.commit()

    total_price = db.session.query(db.func.sum(Product.price * ShoppingCartItem.quantity)).filter(ShoppingCartItem.user_id == user_id).scalar() or 0.0

    return jsonify({'message': 'Product removed successfully', 'total_price': total_price}), 200

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)