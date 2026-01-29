# 🏪 Retail Billing System - Production Ready

A complete, modern retail billing system built with Flask, featuring authentication, discount/VAT calculation, inventory management, and analytics.

## ✨ Features

### 🔐 Authentication & Security
- User signup & login
- Password hashing (Werkzeug)
- Session management
- Protected routes
- Organization isolation

### 💰 Billing & Transactions
- Shopping cart system
- Discount calculation (%)
- VAT calculation (%)
- Real-time total updates
- Invoice generation
- Print-friendly invoices

### 📦 Inventory Management
- Add/Edit/Delete products
- Search functionality
- Pagination (20 items/page)
- Stock level indicators
- Low stock alerts
- AI-powered stock predictions

### 📊 Dashboard & Reports
- Sales analytics
- Today's & weekly sales
- Product statistics
- Transaction history
- Date range filtering
- Export to CSV

### 🎨 Modern UI/UX
- Responsive design
- Toast notifications
- Loading indicators
- Smooth animations
- Color-coded badges
- Professional gradients

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd RetailBillingSystem

# Install dependencies
pip install -r requirements.txt

# Setup database
cd RetailBillingSystem
python setup_db.py

# Run application
python app.py
```

Visit: `http://localhost:5000`

### Demo Account

```
Email: admin@demo.com
Password: admin123
```

## 📁 Project Structure

```
RetailBillingSystem/
├── RetailBillingSystem/
│   ├── models/          # Database models
│   ├── services/        # Business logic
│   ├── static/          # CSS, JS
│   ├── templates/       # HTML templates
│   ├── utils/           # Utilities
│   ├── app.py          # Main application
│   ├── config.py       # Configuration
│   └── setup_db.py     # Database setup
├── requirements.txt    # Dependencies
├── Procfile           # Deployment config
└── DEPLOYMENT.md      # Deployment guide
```

## 🔧 Configuration

Create `.env` file:

```env
SESSION_SECRET=your-secret-key-here
FLASK_ENV=development
DATABASE_URL=sqlite:///retail_billing.db
```

## 📊 Database Schema

- **Users**: Authentication & profiles
- **Organizations**: Multi-tenant support
- **Products**: Inventory items
- **Transactions**: Sales records
- **TransactionItems**: Line items

## 🌐 API Endpoints

### Authentication
- `POST /login` - User login
- `POST /signup` - User registration
- `GET /logout` - User logout

### Products
- `GET /api/products` - List products
- `POST /api/products` - Create product
- `PUT /api/products/<id>` - Update product
- `DELETE /api/products/<id>` - Delete product

### Transactions
- `POST /api/transactions` - Create transaction
- `GET /invoice/<id>` - View invoice

### Predictions
- `GET /api/inventory/predict/<id>` - Stock prediction

## 🚀 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Quick Deploy

**Heroku:**
```bash
heroku create
git push heroku main
heroku run python RetailBillingSystem/setup_db.py
```

**Railway/Render:**
- Connect GitHub repository
- Set environment variables
- Deploy automatically

## 🔒 Security Features

- ✅ Password hashing
- ✅ Session management
- ✅ Input validation
- ✅ SQL injection protection
- ✅ CSRF protection ready
- ✅ Error handling

## 📈 Performance

- Caching (5 min default)
- Pagination
- Debounced search
- Optimized queries
- Lazy loading

## 🎯 Tech Stack

- **Backend**: Flask 2.3.3
- **Database**: SQLAlchemy + SQLite
- **Frontend**: Bootstrap 5, Vanilla JS
- **Caching**: Flask-Caching
- **Deployment**: Gunicorn

## 📝 License

MIT License

## 👨‍💻 Developer

Enhanced by Amazon Q Developer

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📞 Support

For issues or questions:
- Check documentation
- Review deployment guide
- Test with demo account

## 🎉 Acknowledgments

Built with modern web technologies and best practices for production deployment.

---

**Ready for Production!** 🚀
