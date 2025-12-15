from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shopping_cart.db'
db = SQLAlchemy(app)

class ShoppingCart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

@app.route('/modify_quantity', methods=['POST'])
def modify_quantity():
    data = request.json
    user_id = data.get('user_id')
    product_id = data.get('product_id')
    quantity = data.get('quantity')

    if not user_id or not product_id or quantity is None:
        return jsonify({'error': 'User ID, product ID, and quantity are required'}), 400
    if type(quantity) is not int or quantity <= 0:
        return jsonify({'error': 'Quantity must be a positive integer'}), 400

    shopping_cart_item = ShoppingCart.query.filter_by(user_id=user_id, product_id=product_id).first()
    if not shopping_cart_item:
        return jsonify({'error': 'Item not found in the shopping cart'}), 404

    shopping_cart_item.quantity = quantity
    db.session.commit()

    return jsonify({'message': 'Quantity modified successfully', 'total_price': calculate_total_price(user_id)}), 200


def calculate_total_price(user_id):
    items = ShoppingCart.query.filter_by(user_id=user_id).all()
    total_price = 0.0
    for item in items:
        # Assume product price is fetched from Product model, not shown here for brevity
        product_price = 10.0  # Placeholder for actual product price fetching
        total_price += item.quantity * product_price
    return total_price

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)