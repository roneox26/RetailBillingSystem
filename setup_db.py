import sys
sys.path.insert(0, 'e:/RetailBillingSystem/RetailBillingSystem')

from app import app, db
from models.user import Organization, User
from models.product import Product

with app.app_context():
    # Create organization
    org = Organization.query.first()
    if not org:
        org = Organization(name="Demo Store")
        db.session.add(org)
        db.session.commit()
        print("Organization created")
    
    # Create demo user
    if User.query.count() == 0:
        user = User(email="admin@demo.com", name="Admin User", organization_id=org.id)
        user.set_password("admin123")
        db.session.add(user)
        db.session.commit()
        print("Demo user created: admin@demo.com / admin123")
    
    # Create sample products
    if Product.query.count() == 0:
        products = [
            Product(name="Rice 1kg", price=80, stock=100, organization_id=org.id),
            Product(name="Oil 1L", price=150, stock=50, organization_id=org.id),
            Product(name="Sugar 1kg", price=60, stock=75, organization_id=org.id),
            Product(name="Tea 250g", price=120, stock=30, organization_id=org.id),
            Product(name="Salt 1kg", price=25, stock=200, organization_id=org.id),
            Product(name="Flour 1kg", price=55, stock=80, organization_id=org.id),
            Product(name="Milk 1L", price=90, stock=40, organization_id=org.id),
            Product(name="Bread", price=35, stock=60, organization_id=org.id),
        ]
        db.session.add_all(products)
        db.session.commit()
        print(f"{len(products)} products added")
    
    print("\n=== Database setup complete! ===")
    print("Login with: admin@demo.com / admin123")
