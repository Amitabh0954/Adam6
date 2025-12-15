from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
db = SQLAlchemy(app)

product_category = db.Table('product_category',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    categories = db.relationship('Category', secondary=product_category, lazy='subquery', backref=db.backref('products', lazy=True))

    def __repr__(self):
        return f'<Product {self.name}>'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f'<Category {self.name}>'

@app.route('/add_product', methods=['POST'])
def add_product():
    data = request.json
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    category_ids = data.get('categories', [])

    if not name or not description or price is None:
        return jsonify({'error': 'Name, description, and price are required'}), 400
    if type(price) != float or price <= 0:
        return jsonify({'error': 'Price must be a positive number'}), 400

    categories = Category.query.filter(Category.id.in_(category_ids)).all()
    if not categories:
        return jsonify({'error': 'At least one valid category is required'}), 400

    new_product = Product(name=name, description=description, price=price, categories=categories)
    db.session.add(new_product)
    db.session.commit()

    return jsonify({'message': 'Product added successfully'}), 201

@app.route('/add_category', methods=['POST'])
def add_category():
    data = request.json
    name = data.get('name')

    if not name:
        return jsonify({'error': 'Name is required'}), 400

    new_category = Category(name=name)
    db.session.add(new_category)
    db.session.commit()

    return jsonify({'message': 'Category added successfully'}), 201

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)