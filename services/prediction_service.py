import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
from models.transaction import Transaction, TransactionItem
from db import db

_model_cache = {}
_CACHE_TTL_SECONDS = 3600


class PredictionService:
    @staticmethod
    def get_product_sales_history(product_id, days=30):
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        transactions = db.session.query(TransactionItem)\
            .join(Transaction)\
            .filter(
                TransactionItem.product_id == product_id,
                Transaction.date >= start_date,
                Transaction.date <= end_date
            ).all()

        daily_sales = {}
        for item in transactions:
            date = item.transaction.date.date()
            daily_sales[date] = daily_sales.get(date, 0) + item.quantity

        return daily_sales

    @staticmethod
    def predict_future_stock(product_id):
        now = datetime.utcnow()
        cached = _model_cache.get(product_id)
        if cached and (now - cached['timestamp']).seconds < _CACHE_TTL_SECONDS:
            return cached['result']

        sales_history = PredictionService.get_product_sales_history(product_id)

        if len(sales_history) < 2:
            return {
                'prediction': 0,
                'confidence': 0,
                'message': 'Insufficient sales data'
            }

        dates = sorted(sales_history.keys())
        quantities = [sales_history[d] for d in dates]

        X = np.array([(d - dates[0]).days for d in dates]).reshape(-1, 1)
        y = np.array(quantities)

        model = LinearRegression()
        model.fit(X, y)

        next_week = np.array(range(len(X), len(X) + 7)).reshape(-1, 1)
        predictions = model.predict(next_week)

        total_predicted = max(0, round(float(sum(predictions))))
        confidence = min(100, max(0, round(model.score(X, y) * 100)))

        result = {
            'prediction': total_predicted,
            'confidence': confidence,
            'message': f'Predicted need: {total_predicted} units (Confidence: {confidence}%)'
        }

        _model_cache[product_id] = {'result': result, 'timestamp': now}
        return result
