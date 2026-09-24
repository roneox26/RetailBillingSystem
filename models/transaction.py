from datetime import datetime
from db import db
from sqlalchemy import Numeric

class TransactionItem(db.Model):
    __tablename__ = 'transaction_items'

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_time = db.Column(Numeric(10, 2), nullable=False)

    product = db.relationship('Product')

    def get_subtotal(self):
        return self.quantity * self.price_at_time

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    patient_name = db.Column(db.String(100))
    doctor_name = db.Column(db.String(100))
    subtotal = db.Column(Numeric(10, 2), nullable=False, default=0)
    discount_percent = db.Column(Numeric(5, 2), default=0)
    discount_amount = db.Column(Numeric(10, 2), default=0)
    vat_percent = db.Column(Numeric(5, 2), default=0)
    vat_amount = db.Column(Numeric(10, 2), default=0)
    total = db.Column(Numeric(10, 2), nullable=False, default=0)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)

    items = db.relationship('TransactionItem', backref='transaction', lazy=True,
                            cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d %H:%M:%S'),
            'patient_name': self.patient_name or '',
            'doctor_name': self.doctor_name or '',
            'items': [{
                'product_id': item.product_id,
                'product_name': item.product.name if item.product else '',
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
