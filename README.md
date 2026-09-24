# Retail Billing System - Enhanced Version

একটি আধুনিক এবং সম্পূর্ণ Retail Billing System যা Flask দিয়ে তৈরি।

## 🚀 New Features & Improvements

### ✅ Security Enhancements
- ✓ Input validation সব API endpoints এ
- ✓ Better error handling এবং logging
- ✓ Configuration management (dev/production)
- ✓ SQL injection protection (SQLAlchemy ORM)
- ✓ Proper error messages

### 🎨 UI/UX Improvements
- ✓ Modern gradient design
- ✓ Toast notifications (success/error messages)
- ✓ Loading indicators
- ✓ Responsive design (mobile-friendly)
- ✓ Smooth animations
- ✓ Better color scheme
- ✓ Active navigation highlighting

### ⚡ Performance Optimization
- ✓ Flask-Caching implementation
- ✓ Pagination (20 items per page)
- ✓ Search functionality with debounce
- ✓ Optimized database queries

### 📊 New Features
- ✓ **Dashboard** - Sales analytics, statistics
- ✓ **Search** - Product search in inventory
- ✓ **Pagination** - Better data management
- ✓ **Edit/Delete** - Product management
- ✓ **Date Filter** - Reports filtering
- ✓ **Stock Alerts** - Color-coded stock levels
- ✓ **Better Validation** - Form validation

### 🛠️ Code Quality
- ✓ Modular structure (utils, config)
- ✓ Better error handlers
- ✓ Improved logging
- ✓ Code organization
- ✓ Reusable utilities

## 📦 Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## 🔧 Configuration

Create a `.env` file:
```
SESSION_SECRET=your-secret-key-here
FLASK_ENV=development
DATABASE_URL=sqlite:///retail_billing.db
```

## 📱 Features

### 1. Dashboard
- Total products count
- Low stock alerts
- Today's sales
- Weekly sales
- Recent transactions

### 2. Billing
- Quick product selection
- Real-time cart management
- Invoice generation

### 3. Inventory Management
- Add/Edit/Delete products
- Search products
- Pagination
- Stock level indicators
- AI-powered predictions

### 4. Reports
- Transaction history
- Date range filtering
- Pagination
- Export capability

## 🎯 API Endpoints

### Products
- `GET /api/products` - Get all products (with search)
- `POST /api/products` - Create product
- `PUT /api/products/<id>` - Update product
- `DELETE /api/products/<id>` - Delete product

### Transactions
- `POST /api/transactions` - Create transaction
- `GET /invoice/<id>` - View invoice

### Predictions
- `GET /api/inventory/predict/<id>` - Get stock prediction

## 🔐 Security Features

1. **Input Validation** - All inputs validated
2. **Error Handling** - Graceful error management
3. **Logging** - Comprehensive logging
4. **Environment Variables** - Sensitive data protection

## 🎨 UI Components

- Modern gradient buttons
- Animated cards
- Toast notifications
- Loading spinners
- Responsive tables
- Modal dialogs
- Color-coded badges

## 📈 Performance

- Caching (5 min default)
- Pagination (20 items/page)
- Debounced search (500ms)
- Optimized queries

## 🌐 Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## 📝 License

MIT License

## 👨‍💻 Developer

Enhanced by Amazon Q Developer
