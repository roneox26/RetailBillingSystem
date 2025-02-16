import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize SQLAlchemy with a base class
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Configure the database
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise RuntimeError(
        "No DATABASE_URL environment variable set. "
        "Please ensure your database configuration is correct."
    )

logger.info(f"Initializing database with URI: {database_url.split('@')[1]}")  # Log only host/db part
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the database
db.init_app(app)

# Import models after db initialization
from models.product import Product
from models.transaction import Transaction, TransactionItem

# Create database tables
with app.app_context():
    try:
        db.create_all()
        logger.info("Successfully created database tables")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/billing')
def billing():
    products = Product.query.all()
    return render_template('billing.html', products=[p.to_dict() for p in products])

@app.route('/inventory')
def inventory():
    products = Product.query.all()
    return render_template('inventory.html', products=[p.to_dict() for p in products])

@app.route('/reports')
def reports():
    transactions = Transaction.query.all()
    return render_template('reports.html', transactions=[t.to_dict() for t in transactions])

@app.route('/api/products', methods=['GET', 'POST'])
def handle_products():
    if request.method == 'POST':
        try:
            data = request.get_json()
            product = Product(
                name=data['name'],
                price=float(data['price']),
                stock=int(data['stock'])
            )
            db.session.add(product)
            db.session.commit()
            return jsonify({'status': 'success'})
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating product: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 400

    return jsonify([p.to_dict() for p in Product.query.all()])

@app.route('/api/transactions', methods=['POST'])
def create_transaction():
    try:
        data = request.get_json()
        transaction = Transaction(total=float(data['total']))

        for item_data in data['items']:
            product = Product.query.get(item_data['productId'])
            if not product:
                raise ValueError(f"Product {item_data['productId']} not found")

            # Update stock
            product.update_stock(-item_data['quantity'])

            # Create transaction item
            transaction_item = TransactionItem(
                product_id=product.id,
                quantity=item_data['quantity'],
                price_at_time=product.price
            )
            transaction.items.append(transaction_item)

        db.session.add(transaction)
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating transaction: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)