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

    def __repr__(self):
        return f'<ShoppingCart {self.id}>'

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    data = request.json
    user_id = data.get('user_id')
    product_id = data.get('product_id')

    if not user_id or not product_id:
        return jsonify({'error': 'User ID and Product ID are required'}), 400

    cart_item = ShoppingCart.query.filter_by(user_id=user_id, product_id=product_id).first()
    if not cart_item:
        return jsonify({'error': 'Item not found in cart'}), 404

    db.session.delete(cart_item)
    db.session.commit()

    # Calculate the new total price
    cart_items = ShoppingCart.query.filter_by(user_id=user_id).all()
    total_price = sum(item.product_id for item in cart_items) # Simplified for example

    return jsonify({'message': 'Item removed successfully', 'total_price': total_price}), 200

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)