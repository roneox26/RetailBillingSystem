import os
import logging
from datetime import datetime, timedelta, date
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, abort
from flask_caching import Cache
from sqlalchemy import func
from db import db
from config import config
from utils.validators import validate_positive_number, login_required, validate_password
from utils.error_handlers import register_error_handlers

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(config[os.environ.get('FLASK_ENV', 'development')])

cache = Cache(app, config={'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT': 300})

db.init_app(app)

from models.product import Product, MEDICINE_CATEGORIES
from models.transaction import Transaction, TransactionItem
from models.user import User, Organization

with app.app_context():
    db.create_all()
    logger.info("Database tables created")

register_error_handlers(app)

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
            session['org_name'] = user.organization.name
            logger.info(f'User logged in: {email}')
            return jsonify({'status': 'success', 'redirect': url_for('dashboard')})
        return jsonify({'status': 'error', 'message': 'ইমেইল বা পাসওয়ার্ড ভুল'}), 401
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
                return jsonify({'status': 'error', 'message': 'এই ইমেইল ইতিমধ্যে নিবন্ধিত'}), 400

            try:
                validate_password(password)
            except ValueError as ve:
                return jsonify({'status': 'error', 'message': str(ve)}), 400

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
            return jsonify({'status': 'error', 'message': 'নিবন্ধন ব্যর্থ হয়েছে'}), 500
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
@cache.cached(timeout=60, key_prefix=lambda: f'dashboard_{session.get("org_id")}')
def dashboard():
    org_id = session.get('org_id')
    if not org_id:
        return redirect(url_for('login'))
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    expiry_threshold = today + timedelta(days=90)

    total_medicines = Product.query.filter_by(organization_id=org_id).count()
    low_stock = Product.query.filter_by(organization_id=org_id).filter(
        Product.stock <= Product.reorder_level
    ).count()
    expiring_soon = Product.query.filter_by(organization_id=org_id).filter(
        Product.expiry_date <= expiry_threshold,
        Product.expiry_date >= today
    ).count()
    expired = Product.query.filter_by(organization_id=org_id).filter(
        Product.expiry_date < today
    ).count()

    today_sales = db.session.query(func.sum(Transaction.total)).filter(
        Transaction.organization_id == org_id,
        func.date(Transaction.date) == today
    ).scalar() or 0

    week_sales = db.session.query(func.sum(Transaction.total)).filter(
        Transaction.organization_id == org_id,
        Transaction.date >= week_ago
    ).scalar() or 0

    recent_transactions = Transaction.query.filter_by(organization_id=org_id).order_by(
        Transaction.date.desc()
    ).limit(5).all()

    return render_template('dashboard.html',
                           total_medicines=total_medicines,
                           low_stock=low_stock,
                           expiring_soon=expiring_soon,
                           expired=expired,
                           today_sales=today_sales,
                           week_sales=week_sales,
                           recent_transactions=recent_transactions)

@app.route('/billing')
@login_required
def billing():
    org_id = session.get('org_id')
    today = date.today()
    products = Product.query.filter_by(organization_id=org_id).filter(
        Product.stock > 0,
        (Product.expiry_date == None) | (Product.expiry_date >= today)
    ).order_by(Product.name).all()
    return render_template('billing.html', products=[p.to_dict() for p in products])

@app.route('/inventory')
@login_required
def inventory():
    org_id = session.get('org_id')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    filter_type = request.args.get('filter', '')

    query = Product.query.filter_by(organization_id=org_id)
    if search:
        query = query.filter(
            (Product.name.ilike(f'%{search}%')) |
            (Product.generic_name.ilike(f'%{search}%'))
        )
    if category:
        query = query.filter(Product.category == category)
    if filter_type == 'low_stock':
        query = query.filter(Product.stock <= Product.reorder_level)
    elif filter_type == 'expired':
        query = query.filter(Product.expiry_date < date.today())
    elif filter_type == 'expiring':
        threshold = date.today() + timedelta(days=90)
        query = query.filter(Product.expiry_date <= threshold, Product.expiry_date >= date.today())

    pagination = query.order_by(Product.name).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('inventory.html',
                           products=[p.to_dict() for p in pagination.items],
                           pagination=pagination,
                           search=search,
                           category=category,
                           filter_type=filter_type,
                           categories=MEDICINE_CATEGORIES)

@app.route('/reports')
@login_required
def reports():
    org_id = session.get('org_id')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    query = Transaction.query.filter_by(organization_id=org_id)
    if date_from:
        query = query.filter(Transaction.date >= datetime.strptime(date_from, '%Y-%m-%d'))
    if date_to:
        query = query.filter(Transaction.date <= datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1))

    total_amount = query.with_entities(func.sum(Transaction.total)).scalar() or 0
    pagination = query.order_by(Transaction.date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('reports.html', transactions=pagination.items,
                           pagination=pagination, total_amount=total_amount)

# ── Medicine (Product) API ──────────────────────────────────────────────────

@app.route('/api/products', methods=['GET', 'POST'])
@login_required
def handle_products():
    org_id = session.get('org_id')
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'status': 'error', 'message': 'কোনো ডেটা পাওয়া যায়নি'}), 400

            name = data.get('name', '').strip()
            if not name or len(name) < 2:
                return jsonify({'status': 'error', 'message': 'ওষুধের নাম দিন (কমপক্ষে ২ অক্ষর)'}), 400

            price = validate_positive_number(data.get('price'), 'বিক্রয় মূল্য')
            stock = int(data.get('stock', 0))
            if stock < 0:
                return jsonify({'status': 'error', 'message': 'স্টক ঋণাত্মক হতে পারবে না'}), 400

            expiry_date = None
            if data.get('expiry_date'):
                expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()

            purchase_price = None
            if data.get('purchase_price'):
                purchase_price = validate_positive_number(data['purchase_price'], 'ক্রয় মূল্য')

            product = Product(
                name=name,
                generic_name=data.get('generic_name', '').strip() or None,
                category=data.get('category', 'Tablet'),
                manufacturer=data.get('manufacturer', '').strip() or None,
                batch_no=data.get('batch_no', '').strip() or None,
                expiry_date=expiry_date,
                price=price,
                purchase_price=purchase_price,
                stock=stock,
                reorder_level=int(data.get('reorder_level', 10)),
                organization_id=org_id
            )
            db.session.add(product)
            db.session.commit()
            cache.clear()
            logger.info(f'Medicine added: {name}')
            return jsonify({'status': 'success', 'product': product.to_dict()})
        except ValueError as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error adding medicine: {str(e)}')
            return jsonify({'status': 'error', 'message': 'ওষুধ যোগ করতে ব্যর্থ'}), 500

    search = request.args.get('search', '')
    query = Product.query.filter_by(organization_id=org_id)
    if search:
        query = query.filter(
            (Product.name.ilike(f'%{search}%')) |
            (Product.generic_name.ilike(f'%{search}%'))
        )
    return jsonify([p.to_dict() for p in query.order_by(Product.name).all()])

@app.route('/api/products/<int:product_id>', methods=['PUT', 'DELETE'])
@login_required
def manage_product(product_id):
    org_id = session.get('org_id')
    product = Product.query.filter_by(id=product_id, organization_id=org_id).first_or_404()

    if request.method == 'PUT':
        try:
            data = request.get_json()
            if 'name' in data:
                product.name = data['name'].strip()
            if 'generic_name' in data:
                product.generic_name = data['generic_name'].strip() or None
            if 'category' in data:
                product.category = data['category']
            if 'manufacturer' in data:
                product.manufacturer = data['manufacturer'].strip() or None
            if 'batch_no' in data:
                product.batch_no = data['batch_no'].strip() or None
            if 'expiry_date' in data and data['expiry_date']:
                product.expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
            if 'price' in data:
                product.price = validate_positive_number(data['price'], 'বিক্রয় মূল্য')
            if 'purchase_price' in data and data['purchase_price']:
                product.purchase_price = validate_positive_number(data['purchase_price'], 'ক্রয় মূল্য')
            if 'stock' in data:
                product.stock = int(data['stock'])
            if 'reorder_level' in data:
                product.reorder_level = int(data['reorder_level'])
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

# ── Transaction API ─────────────────────────────────────────────────────────

@app.route('/api/transactions', methods=['POST'])
@login_required
def create_transaction():
    try:
        data = request.get_json()
        if not data or 'items' not in data or not data['items']:
            return jsonify({'status': 'error', 'message': 'কোনো আইটেম নেই'}), 400

        org_id = session.get('org_id')
        subtotal = 0
        transaction = Transaction(
            organization_id=org_id,
            patient_name=data.get('patient_name', '').strip() or None,
            doctor_name=data.get('doctor_name', '').strip() or None,
        )

        for item_data in data['items']:
            product = Product.query.filter_by(id=item_data.get('productId'), organization_id=org_id).first()
            if not product:
                return jsonify({'status': 'error', 'message': f"ওষুধ পাওয়া যায়নি"}), 404
            if product.is_expired:
                return jsonify({'status': 'error', 'message': f'{product.name} মেয়াদোত্তীর্ণ'}), 400

            quantity = int(item_data.get('quantity', 0))
            if quantity <= 0:
                return jsonify({'status': 'error', 'message': 'পরিমাণ সঠিক নয়'}), 400
            if product.stock < quantity:
                return jsonify({'status': 'error', 'message': f'{product.name} — পর্যাপ্ত স্টক নেই'}), 400

            product.update_stock(-quantity)
            transaction.items.append(TransactionItem(
                product_id=product.id,
                quantity=quantity,
                price_at_time=product.price
            ))
            subtotal += product.price * quantity

        transaction.subtotal = subtotal
        discount_percent = max(0, min(100, float(data.get('discount_percent', 0))))
        vat_percent = max(0, min(100, float(data.get('vat_percent', 0))))

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
        return jsonify({'status': 'error', 'message': 'বিক্রয় সম্পন্ন হয়নি'}), 500

# ── Invoice ─────────────────────────────────────────────────────────────────

@app.route('/invoice/<int:transaction_id>')
@login_required
def invoice(transaction_id):
    org_id = session.get('org_id')
    transaction = Transaction.query.filter_by(id=transaction_id, organization_id=org_id).first_or_404()
    org = Organization.query.get(org_id)
    return render_template('invoice.html', transaction=transaction, org=org)

# ── Alerts API ───────────────────────────────────────────────────────────────

@app.route('/api/alerts')
@login_required
def get_alerts():
    org_id = session.get('org_id')
    today = date.today()
    threshold = today + timedelta(days=90)

    expired = Product.query.filter_by(organization_id=org_id).filter(
        Product.expiry_date < today, Product.stock > 0
    ).all()
    expiring = Product.query.filter_by(organization_id=org_id).filter(
        Product.expiry_date <= threshold, Product.expiry_date >= today
    ).all()
    low_stock = Product.query.filter_by(organization_id=org_id).filter(
        Product.stock <= Product.reorder_level, Product.stock > 0
    ).all()
    out_of_stock = Product.query.filter_by(organization_id=org_id, stock=0).all()

    return jsonify({
        'expired': [p.to_dict() for p in expired],
        'expiring_soon': [p.to_dict() for p in expiring],
        'low_stock': [p.to_dict() for p in low_stock],
        'out_of_stock': [p.to_dict() for p in out_of_stock],
    })

# ── Prediction ───────────────────────────────────────────────────────────────

from services.prediction_service import PredictionService

@app.route('/api/inventory/predict/<int:product_id>')
@login_required
def predict_inventory(product_id):
    org_id = session.get('org_id')
    product = Product.query.filter_by(id=product_id, organization_id=org_id).first_or_404()
    try:
        prediction = PredictionService.predict_future_stock(product.id)
        return jsonify(prediction)
    except Exception as e:
        logger.error(f'Prediction error for product {product_id}: {str(e)}')
        return jsonify({'error': 'Prediction failed'}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
