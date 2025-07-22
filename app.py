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
    # Build URL from individual components if DATABASE_URL is not set
    pg_user = os.environ.get("PGUSER")
    pg_password = os.environ.get("PGPASSWORD")
    pg_host = os.environ.get("PGHOST")
    pg_port = os.environ.get("PGPORT")
    pg_database = os.environ.get("PGDATABASE")
    
    if all([pg_user, pg_password, pg_host, pg_port, pg_database]):
        database_url = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}"
    else:
        raise RuntimeError(
            "No DATABASE_URL or complete PostgreSQL environment variables set. "
            "Please ensure your database configuration is correct."
        )

# Only log the non-sensitive part of the URL to avoid exposing credentials
safe_db_url = database_url.split('@')[1] if '@' in database_url else "unknown"
logger.info(f"Initializing database with URI host/db: {safe_db_url}")  
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
    "pool_timeout": 20,
    "pool_size": 10,
    "max_overflow": 20,
    "connect_args": {
        "sslmode": "require",
        "connect_timeout": 10
    }
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

# Import PredictionService after models are loaded
from services.prediction_service import PredictionService

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
            product = Product()
            product.name = data['name']
            product.price = float(data['price'])
            product.stock = int(data['stock'])
            db.session.add(product)
            db.session.commit()
            return jsonify({'status': 'success'})
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating product: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 400

    return jsonify([p.to_dict() for p in Product.query.all()])

@app.route('/invoice/<int:transaction_id>')
def invoice(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    return render_template('invoice.html', transaction=transaction)

@app.route('/api/transactions', methods=['POST'])
def create_transaction():
    try:
        data = request.get_json()
        transaction = Transaction()
        transaction.total = float(data['total'])

        for item_data in data['items']:
            product = Product.query.get(item_data['productId'])
            if not product:
                raise ValueError(f"Product {item_data['productId']} not found")

            # Update stock
            product.update_stock(-item_data['quantity'])

            # Create transaction item
            transaction_item = TransactionItem()
            transaction_item.product_id = product.id
            transaction_item.quantity = item_data['quantity']
            transaction_item.price_at_time = product.price
            transaction.items.append(transaction_item)

        db.session.add(transaction)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'transaction_id': transaction.id
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating transaction: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/inventory/predict/<int:product_id>')
def predict_inventory(product_id):
    """Get inventory predictions for a product"""
    try:
        prediction = PredictionService.predict_future_stock(product_id)
        return jsonify(prediction)
    except Exception as e:
        logging.error(f"Error predicting inventory: {str(e)}")
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)