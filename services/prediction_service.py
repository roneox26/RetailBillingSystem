import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
from models.transaction import Transaction, TransactionItem
from models.product import Product
from db import db

class PredictionService:
    @staticmethod
    def get_product_sales_history(product_id, days=30):
        """Get daily sales data for a product over the specified period"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query all transactions within the date range
        transactions = db.session.query(TransactionItem)\
            .join(Transaction)\
            .filter(
                TransactionItem.product_id == product_id,
                Transaction.date >= start_date,
                Transaction.date <= end_date
            ).all()
        
        # Aggregate sales by date
        daily_sales = {}
        for item in transactions:
            date = item.transaction.date.date()
            daily_sales[date] = daily_sales.get(date, 0) + item.quantity
        
        return daily_sales

    @staticmethod
    def predict_future_stock(product_id):
        """Predict future stock needs based on historical sales data"""
        sales_history = PredictionService.get_product_sales_history(product_id)
        
        if not sales_history:
            return {
                'prediction': 0,
                'confidence': 0,
                'message': 'Insufficient sales data'
            }
        
        # Convert daily sales to a time series
        dates = list(sales_history.keys())
        quantities = list(sales_history.values())
        
        # Create features (days from start)
        X = np.array([(date - dates[0]).days for date in dates]).reshape(-1, 1)
        y = np.array(quantities)
        
        # Fit linear regression model
        model = LinearRegression()
        model.fit(X, y)
        
        # Predict next 7 days
        next_week = np.array(range(len(X), len(X) + 7)).reshape(-1, 1)
        predictions = model.predict(next_week)
        
        # Calculate total predicted sales for next week
        total_predicted = max(0, round(sum(predictions)))
        confidence = min(100, max(0, round(model.score(X, y) * 100)))
        
        return {
            'prediction': total_predicted,
            'confidence': confidence,
            'message': f'Predicted need: {total_predicted} units (Confidence: {confidence}%)'
        }
