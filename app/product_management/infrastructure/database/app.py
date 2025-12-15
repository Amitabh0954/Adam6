from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))

    def __repr__(self):
        return f'<Product {self.name}>'

@app.route('/search_products', methods=['GET'])
def search_products():
    search_query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    search = "%{}%".format(search_query)
    products = Product.query.filter(or_(Product.name.ilike(search), Product.description.ilike(search), Product.category.ilike(search))).paginate(page, per_page, False)

    result = []
    for product in products.items:
        result.append({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'category': product.category
        })

    return jsonify({
        'products': result,
        'total': products.total,
        'pages': products.pages,
        'current_page': products.page
    }), 200

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)