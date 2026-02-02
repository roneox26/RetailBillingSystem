from datetime import datetime
from db import db

class Product(db.Model):
    """Model for products in inventory"""
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.name}>'

    def to_dict(self):
        """Convert product to dictionary format"""
        return {
            'id': self.id,
            'name': self.name,
            'price': float(self.price),
            'stock': self.stock
        }

    def update_stock(self, quantity_change):
        """Update product stock"""
        new_stock = self.stock + quantity_change
        if new_stock < 0:
            raise ValueError("Insufficient stock")
        self.stock = new_stock
        self.updated_at = datetime.utcnow()