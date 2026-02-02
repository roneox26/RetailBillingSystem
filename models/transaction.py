from datetime import datetime
from db import db

class TransactionItem(db.Model):
    """Model for individual items in a transaction"""
    __tablename__ = 'transaction_items'

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_time = db.Column(db.Float, nullable=False)

    product = db.relationship('Product')

    def __repr__(self):
        return f'<TransactionItem {self.id}>'

    def get_subtotal(self):
        """Calculate subtotal for this item"""
        return self.quantity * self.price_at_time

class Transaction(db.Model):
    """Model for transactions/bills"""
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    subtotal = db.Column(db.Float, nullable=False, default=0)
    discount_percent = db.Column(db.Float, default=0)
    discount_amount = db.Column(db.Float, default=0)
    vat_percent = db.Column(db.Float, default=0)
    vat_amount = db.Column(db.Float, default=0)
    total = db.Column(db.Float, nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)

    items = db.relationship('TransactionItem', backref='transaction', lazy=True,
                          cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Transaction {self.id}>'

    def to_dict(self):
        """Convert transaction to dictionary format"""
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d %H:%M:%S'),
            'items': [{
                'product_id': item.product_id,
                'quantity': item.quantity,
                'price': float(item.price_at_time),
                'subtotal': float(item.get_subtotal())
            } for item in self.items],
            'subtotal': float(self.subtotal),
            'discount_percent': float(self.discount_percent),
            'discount_amount': float(self.discount_amount),
            'vat_percent': float(self.vat_percent),
            'vat_amount': float(self.vat_amount),
            'total': float(self.total)
        }

    def calculate_total(self):
        """Calculate total for the entire transaction"""
        self.subtotal = sum(item.get_subtotal() for item in self.items)
        after_discount = self.subtotal - self.discount_amount
        self.total = after_discount + self.vat_amount
        return self.total
