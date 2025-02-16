import os
import csv
from datetime import datetime
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Data storage paths
PRODUCTS_FILE = 'data/products.csv'
TRANSACTIONS_FILE = 'data/transactions.csv'

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Initialize CSV files if they don't exist
if not os.path.exists(PRODUCTS_FILE):
    with open(PRODUCTS_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'name', 'price', 'stock'])

if not os.path.exists(TRANSACTIONS_FILE):
    with open(TRANSACTIONS_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'date', 'items', 'total'])

def get_products():
    products = []
    with open(PRODUCTS_FILE, 'r') as f:
        reader = csv.DictReader(f)
        products = list(reader)
    return products

def get_transactions():
    transactions = []
    with open(TRANSACTIONS_FILE, 'r') as f:
        reader = csv.DictReader(f)
        transactions = list(reader)
    return transactions

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/billing')
def billing():
    products = get_products()
    return render_template('billing.html', products=products)

@app.route('/inventory')
def inventory():
    products = get_products()
    return render_template('inventory.html', products=products)

@app.route('/reports')
def reports():
    transactions = get_transactions()
    return render_template('reports.html', transactions=transactions)

@app.route('/api/products', methods=['GET', 'POST'])
def handle_products():
    if request.method == 'POST':
        data = request.get_json()
        products = get_products()
        new_id = str(len(products) + 1)
        
        with open(PRODUCTS_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([new_id, data['name'], data['price'], data['stock']])
        
        return jsonify({'status': 'success'})
    
    return jsonify(get_products())

@app.route('/api/transactions', methods=['POST'])
def create_transaction():
    data = request.get_json()
    transactions = get_transactions()
    new_id = str(len(transactions) + 1)
    
    with open(TRANSACTIONS_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            new_id,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            str(data['items']),
            data['total']
        ])
    
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
