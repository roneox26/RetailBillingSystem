from datetime import datetime
from app import db

class TransactionItem(db.Model):
    """Model for individual items in a transaction"""
    __tablename__ = 'transaction_items'

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_time = db.Column(db.Float, nullable=False)

    # Add relationship to Product for invoice details
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
    total = db.Column(db.Float, nullable=False)

    # Relationship with TransactionItem
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
            'total': float(self.total)
        }

    def calculate_total(self):
        """Calculate total for the entire transaction"""
        self.total = sum(item.get_subtotal() for item in self.items)
        return self.total