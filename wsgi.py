import sys
import os

# Add RetailBillingSystem to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'RetailBillingSystem'))

from app import app

if __name__ == "__main__":
    app.run()
