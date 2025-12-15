from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///product_management.db'
app.config['SECRET_KEY'] = os.urandom(24)

db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f'<Product {self.name}>'

@app.route('/search_products', methods=['GET'])
def search_products():
    query = request.args.get('query')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if not query:
        return jsonify({'error': 'Search query is required'}), 400

    search = f'%{query}%'
    products = Product.query.filter(
        (Product.name.ilike(search)) | 
        (Product.category.ilike(search)) | 
        (Product.description.ilike(search))
    ).paginate(page=page, per_page=per_page)

    result = {
        'products': [
            {
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': product.price,
                'category': product.category,
            } for product in products.items
        ],
        'total': products.total,
        'pages': products.pages,
        'current_page': products.page,
        'has_next': products.has_next,
        'has_prev': products.has_prev,
    }

    return jsonify(result)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)