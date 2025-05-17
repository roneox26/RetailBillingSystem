"""
Script to populate the database with sample data for the POS system.
"""
import random
from datetime import datetime, timedelta
from app import app, db
from models.product import Product
from models.transaction import Transaction, TransactionItem

def clear_existing_data():
    """Clear existing data from the database."""
    print("Clearing existing data...")
    TransactionItem.query.delete()
    Transaction.query.delete()
    Product.query.delete()
    db.session.commit()
    print("Existing data cleared.")

def create_sample_products():
    """Create sample products."""
    print("Creating sample products...")
    products = []
    
    # Create each product individually
    p1 = Product()
    p1.name = "Coffee"
    p1.price = 3.50
    p1.stock = 100
    products.append(p1)
    
    p2 = Product()
    p2.name = "Tea"
    p2.price = 2.50
    p2.stock = 150
    products.append(p2)
    
    p3 = Product()
    p3.name = "Sandwich"
    p3.price = 5.99
    p3.stock = 30
    products.append(p3)
    
    p4 = Product()
    p4.name = "Salad"
    p4.price = 7.99
    p4.stock = 20
    products.append(p4)
    
    p5 = Product()
    p5.name = "Muffin"
    p5.price = 2.99
    p5.stock = 40
    products.append(p5)
    
    p6 = Product()
    p6.name = "Cookie"
    p6.price = 1.99
    p6.stock = 50
    products.append(p6)
    
    p7 = Product()
    p7.name = "Water Bottle"
    p7.price = 1.50
    p7.stock = 200
    products.append(p7)
    
    p8 = Product()
    p8.name = "Juice"
    p8.price = 3.99
    p8.stock = 75
    products.append(p8)
    
    p9 = Product()
    p9.name = "Energy Bar"
    p9.price = 2.49
    p9.stock = 60
    products.append(p9)
    
    p10 = Product()
    p10.name = "Chips"
    p10.price = 1.79
    p10.stock = 85
    products.append(p10)
    
    db.session.add_all(products)
    db.session.commit()
    print(f"Created {len(products)} sample products.")
    return products

def create_sample_transactions(products, num_transactions=15):
    """Create sample transactions."""
    print(f"Creating {num_transactions} sample transactions...")
    
    transactions = []
    now = datetime.utcnow()
    
    for i in range(num_transactions):
        # Create a transaction between 1 and 30 days ago
        transaction_date = now - timedelta(days=random.randint(1, 30), 
                                          hours=random.randint(0, 23),
                                          minutes=random.randint(0, 59))
        
        # Randomly select 1-5 products for this transaction
        num_items = random.randint(1, 5)
        selected_products = random.sample(products, num_items)
        
        # Create the transaction
        transaction = Transaction()
        transaction.date = transaction_date
        transaction.total = 0  # Initial value, will update later
        
        # Add items to the transaction
        total = 0
        for product in selected_products:
            quantity = random.randint(1, 3)
            price = product.price
            
            # Create transaction item
            transaction_item = TransactionItem()
            transaction_item.product_id = product.id
            transaction_item.quantity = quantity
            transaction_item.price_at_time = price
            
            transaction.items.append(transaction_item)
            
            # Add to total
            total += price * quantity
        
        transaction.total = total
        transactions.append(transaction)
    
    db.session.add_all(transactions)
    db.session.commit()
    
    print(f"Created {len(transactions)} sample transactions with a total of "
          f"{sum(len(t.items) for t in transactions)} items.")
    return transactions

def main():
    """Main function to populate the database."""
    with app.app_context():
        clear_existing_data()
        products = create_sample_products()
        create_sample_transactions(products)
        print("Sample data creation complete!")

if __name__ == "__main__":
    main()