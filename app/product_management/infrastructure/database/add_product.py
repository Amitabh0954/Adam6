from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///product_management.db'
app.config['SECRET_KEY'] = os.urandom(24)

db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Product {self.name}>'

@app.route('/add_product', methods=['POST'])
def add_product():
    data = request.json
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')

    if not name or not description or price is None:
        return jsonify({'error': 'Name, description, and price are required'}), 400

    if price <= 0:
        return jsonify({'error': 'Price must be a positive number'}), 400

    existing_product = Product.query.filter_by(name=name).first()
    if existing_product:
        return jsonify({'error': 'Product name must be unique'}), 409

    new_product = Product(name=name, description=description, price=price)
    db.session.add(new_product)
    db.session.commit()

    return jsonify({'message': 'Product added successfully'}), 201

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
