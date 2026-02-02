import os
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_caching import Cache
from sqlalchemy import func
from db import db
from config import config
from utils.validators import validate_json, validate_positive_number, login_required

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(config[os.environ.get('FLASK_ENV', 'development')])

cache = Cache(app, config={'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT': 300})

db.init_app(app)

from models.product import Product
from models.transaction import Transaction, TransactionItem
from models.user import User, Organization

with app.app_context():
    db.create_all()
    logger.info("Database tables created")

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['org_id'] = user.organization_id
            logger.info(f'User logged in: {email}')
            return jsonify({'status': 'success', 'redirect': url_for('dashboard')})
        return jsonify({'status': 'error', 'message': 'Invalid email or password'}), 401
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            data = request.get_json()
            email = data.get('email', '').strip()
            password = data.get('password', '')
            name = data.get('name', '').strip()
            org_name = data.get('org_name', '').strip()
            
            if User.query.filter_by(email=email).first():
                return jsonify({'status': 'error', 'message': 'Email already exists'}), 400
            
            org = Organization(name=org_name)
            db.session.add(org)
            db.session.flush()
            
            user = User(email=email, name=name, organization_id=org.id)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            logger.info(f'New user registered: {email}')
            return jsonify({'status': 'success', 'redirect': url_for('login')})
        except Exception as e:
            db.session.rollback()
            logger.error(f'Signup error: {str(e)}')
            return jsonify({'status': 'error', 'message': 'Registration failed'}), 500
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
@cache.cached(timeout=60)
def dashboard():
    org_id = session.get('org_id', 1)
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    
    total_products = Product.query.filter_by(organization_id=org_id).count()
    low_stock = Product.query.filter_by(organization_id=org_id).filter(Product.stock < 10).count()
    
    today_sales = db.session.query(func.sum(Transaction.total)).filter(
        Transaction.organization_id == org_id,
        func.date(Transaction.date) == today
    ).scalar() or 0
    
    week_sales = db.session.query(func.sum(Transaction.total)).filter(
        Transaction.organization_id == org_id,
        Transaction.date >= week_ago
    ).scalar() or 0
    
    recent_transactions = Transaction.query.filter_by(organization_id=org_id).order_by(Transaction.date.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         total_products=total_products,
                         low_stock=low_stock,
                         today_sales=today_sales,
                         week_sales=week_sales,
                         recent_transactions=recent_transactions)

@app.route('/billing')
@login_required
def billing():
    org_id = session.get('org_id', 1)
    products = Product.query.filter_by(organization_id=org_id).all()
    return render_template('billing.html', products=[p.to_dict() for p in products])

@app.route('/inventory')
@login_required
def inventory():
    org_id = session.get('org_id', 1)
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('search', '')
    
    query = Product.query.filter_by(organization_id=org_id)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('inventory.html', products=[p.to_dict() for p in pagination.items], 
                         pagination=pagination, search=search)

@app.route('/reports')
@login_required
def reports():
    org_id = session.get('org_id', 1)
    page = request.args.get('page', 1, type=int)
    per_page = 20
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    query = Transaction.query.filter_by(organization_id=org_id)
    if date_from:
        query = query.filter(Transaction.date >= datetime.strptime(date_from, '%Y-%m-%d'))
    if date_to:
        query = query.filter(Transaction.date <= datetime.strptime(date_to, '%Y-%m-%d'))
    
    pagination = query.order_by(Transaction.date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('reports.html', transactions=pagination.items, pagination=pagination)

@app.route('/api/products', methods=['GET', 'POST'])
@login_required
def handle_products():
    org_id = session.get('org_id', 1)
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'status': 'error', 'message': 'No data provided'}), 400
            
            name = data.get('name', '').strip()
            if not name or len(name) < 2:
                return jsonify({'status': 'error', 'message': 'Product name required (min 2 chars)'}), 400
            
            price = validate_positive_number(data.get('price'), 'Price')
            stock = int(data.get('stock', 0))
            if stock < 0:
                return jsonify({'status': 'error', 'message': 'Stock cannot be negative'}), 400
            
            product = Product(name=name, price=price, stock=stock, organization_id=org_id)
            db.session.add(product)
            db.session.commit()
            cache.clear()
            logger.info(f'Product created: {name}')
            return jsonify({'status': 'success', 'product': product.to_dict()})
        except ValueError as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error creating product: {str(e)}')
            return jsonify({'status': 'error', 'message': 'Failed to create product'}), 500
    
    search = request.args.get('search', '')
    query = Product.query.filter_by(organization_id=org_id)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    return jsonify([p.to_dict() for p in query.all()])

@app.route('/invoice/<int:transaction_id>')
def invoice(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    return render_template('invoice.html', transaction=transaction)

@app.route('/api/transactions', methods=['POST'])
@login_required
def create_transaction():
    try:
        data = request.get_json()
        if not data or 'items' not in data or not data['items']:
            return jsonify({'status': 'error', 'message': 'No items in transaction'}), 400
        
        subtotal = 0
        transaction = Transaction(organization_id=session.get('org_id', 1))

        for item_data in data['items']:
            product = Product.query.get(item_data.get('productId'))
            if not product:
                return jsonify({'status': 'error', 'message': f"Product {item_data.get('productId')} not found"}), 404
            
            quantity = int(item_data.get('quantity', 0))
            if quantity <= 0:
                return jsonify({'status': 'error', 'message': 'Invalid quantity'}), 400
            
            if product.stock < quantity:
                return jsonify({'status': 'error', 'message': f'Insufficient stock for {product.name}'}), 400
            
            product.update_stock(-quantity)
            transaction_item = TransactionItem(
                product_id=product.id,
                quantity=quantity,
                price_at_time=product.price
            )
            transaction.items.append(transaction_item)
            subtotal += product.price * quantity
        
        # Calculate discount and VAT
        transaction.subtotal = subtotal
        discount_percent = float(data.get('discount_percent', 0))
        vat_percent = float(data.get('vat_percent', 0))
        
        transaction.discount_percent = discount_percent
        transaction.discount_amount = (subtotal * discount_percent) / 100
        
        after_discount = subtotal - transaction.discount_amount
        transaction.vat_percent = vat_percent
        transaction.vat_amount = (after_discount * vat_percent) / 100
        
        transaction.total = after_discount + transaction.vat_amount

        db.session.add(transaction)
        db.session.commit()
        cache.clear()
        logger.info(f'Transaction created: {transaction.id}')
        return jsonify({'status': 'success', 'transaction_id': transaction.id})
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f'Transaction error: {str(e)}')
        return jsonify({'status': 'error', 'message': 'Transaction failed'}), 500

from services.prediction_service import PredictionService

@app.route('/api/inventory/predict/<int:product_id>')
def predict_inventory(product_id):
    try:
        prediction = PredictionService.predict_future_stock(product_id)
        return jsonify(prediction)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['PUT', 'DELETE'])
@login_required
def manage_product(product_id):
    org_id = session.get('org_id', 1)
    product = Product.query.filter_by(id=product_id, organization_id=org_id).first_or_404()
    
    if request.method == 'PUT':
        try:
            data = request.get_json()
            if 'name' in data:
                product.name = data['name'].strip()
            if 'price' in data:
                product.price = validate_positive_number(data['price'], 'Price')
            if 'stock' in data:
                product.stock = int(data['stock'])
            
            db.session.commit()
            cache.clear()
            return jsonify({'status': 'success', 'product': product.to_dict()})
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 400
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(product)
            db.session.commit()
            cache.clear()
            return jsonify({'status': 'success'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 400

@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({'status': 'error', 'message': 'Resource not found'}), 404
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if request.path.startswith('/api/'):
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500
    return render_template('index.html'), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
