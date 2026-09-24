from datetime import datetime, date
from db import db
from sqlalchemy import Numeric

MEDICINE_CATEGORIES = [
    'Tablet', 'Capsule', 'Syrup', 'Injection', 'Cream/Ointment',
    'Eye/Ear Drop', 'Inhaler', 'Suppository', 'Powder', 'Other'
]

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    generic_name = db.Column(db.String(150))
    category = db.Column(db.String(50), default='Tablet')
    manufacturer = db.Column(db.String(100))
    batch_no = db.Column(db.String(50))
    expiry_date = db.Column(db.Date)
    price = db.Column(Numeric(10, 2), nullable=False)
    purchase_price = db.Column(Numeric(10, 2))
    stock = db.Column(db.Integer, nullable=False, default=0)
    reorder_level = db.Column(db.Integer, default=10)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Medicine {self.name}>'

    @property
    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date < date.today()
        return False

    @property
    def is_expiring_soon(self):
        if self.expiry_date:
            days_left = (self.expiry_date - date.today()).days
            return 0 <= days_left <= 90
        return False

    @property
    def days_to_expiry(self):
        if self.expiry_date:
            return (self.expiry_date - date.today()).days
        return None

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'generic_name': self.generic_name or '',
            'category': self.category or '',
            'manufacturer': self.manufacturer or '',
            'batch_no': self.batch_no or '',
            'expiry_date': self.expiry_date.strftime('%Y-%m-%d') if self.expiry_date else '',
            'price': float(self.price),
            'purchase_price': float(self.purchase_price) if self.purchase_price else 0,
            'stock': self.stock,
            'reorder_level': self.reorder_level,
            'is_expired': self.is_expired,
            'is_expiring_soon': self.is_expiring_soon,
            'days_to_expiry': self.days_to_expiry,
        }

    def update_stock(self, quantity_change):
        new_stock = self.stock + quantity_change
        if new_stock < 0:
            raise ValueError(f"অপর্যাপ্ত স্টক: {self.name}")
        self.stock = new_stock
        self.updated_at = datetime.utcnow()
