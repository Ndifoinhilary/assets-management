A comprehensive,
asset management system built with Django REST Framework featuring advanced analytics, reporting, and real-time dashboard capabilities.

## 🚀 Features

### Core Functionality
- **Comprehensive Asset Management**: Track stocks, bonds, cryptocurrencies, real estate, and more
- **Advanced Transaction System**: Buy/sell orders with multiple order types (market, limit, stop)
- **Portfolio Analytics**: Real-time performance tracking and profit/loss calculations
- **Reporting System**: Configurable reports with multiple export formats
- **Dashboard Analytics**: Interactive graphs and charts for data visualization
- **User Management**: Role-based access control with detailed permissions

### Technical Features
- **RESTful API**: Fully documented with OpenAPI/Swagger
- **Advanced Filtering**: Search, filter, and pagination across all endpoints
- **Data Validation**: Comprehensive validation with custom business rules
- **Error Handling**: Detailed error responses with proper HTTP status codes
- **Performance Optimized**: Database query optimization and caching support
- **Security**: JWT authentication with role-based permissions
- **Extensible**: Modular design for easy feature additions

## 📊 API Endpoints

### Core Resources

#### Assets
- `GET /api/v1/assets/` - List all assets with filtering
- `POST /api/v1/assets/` - Create new asset
- `GET /api/v1/assets/{id}/` - Get asset details
- `PUT /api/v1/assets/{id}/` - Update asset
- `DELETE /api/v1/assets/{id}/` - Delete asset
- `POST /api/v1/assets/{id}/update_price/` - Update asset price
- `GET /api/v1/assets/{id}/statistics/` - Get asset statistics

#### Transactions
- `GET /api/v1/transactions/` - List transactions with filtering
- `POST /api/v1/transactions/` - Record new transaction
- `GET /api/v1/transactions/{id}/` - Get transaction details
- `GET /api/v1/transactions/summary/` - Get user transaction summary

#### Reports
- `GET /api/v1/reports/` - List generated reports
- `POST /api/v1/reports/` - Generate new report
- `GET /api/v1/reports/{id}/` - Get report details

#### Analytics (Dashboard)
- `GET /api/v1/analytics/graphs/` - **Main dashboard endpoint**
- `GET /api/v1/analytics/available_graphs/` - Available graph types

### Asset Categories
- `GET /api/v1/categories/` - List asset categories
- `POST /api/v1/categories/` - Create category
- `GET /api/v1/categories/{id}/` - Get category details

## 📈 Analytics Dashboard

The analytics endpoint provides comprehensive data for dashboard visualization:

```bash
# Get all dashboard data
GET /api/v1/analytics/graphs/

# Get specific graph with time filter
GET /api/v1/analytics/graphs/?graph_type=user_growth&days=60

# Available graph types
GET /api/v1/analytics/available_graphs/
```

### Graph Types Available:
1. **User Growth** - Registration trends over time
2. **Asset Distribution** - Distribution by type, value, and market cap
3. **Transaction Volume** - Daily trading volume and patterns
4. **Portfolio Performance** - Individual user performance metrics
5. **Asset Type Performance** - Performance grouped by asset categories
6. **Top Assets** - Most actively traded assets
7. **Transaction Trends** - Patterns and trends by transaction type

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Git

### Quick Start

1. **Clone the repository**
```bash
git clone git@github.com:Ndifoinhilary/assets-management.git

or 
git clone https://github.com/Ndifoinhilary/assets-management.git

cd asset-management
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment setup**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Database setup**
```bash
# Create PostgreSQL database
createdb asset_management

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

6. **Start development server**
```bash
python manage.py runserver
```

### Access Points
- **API Documentation**: http://localhost:8000/api/docs/
- **ReDoc Documentation**: http://localhost:8000/api/redoc/
- **Admin Interface**: http://localhost:8000/admin/

## 📖 API Documentation

### Interactive Documentation
Visit `/api/docs/` for interactive Swagger UI documentation where you can:
- Explore all endpoints
- Test API calls directly
- View request/response schemas
- Authenticate and make real requests

### Authentication
All endpoints require authentication. Use JWT  Authentication:

```bash
# Get token (after creating user)
POST /api/auth/token/
{
    "username": "your_username",
    "email": "your_email"
    "password": "your_password"
    "confirm_password":"your_password"
}

# Use token in requests
curl -H "Authorization: Token your_token_here" \
     http://localhost:8000/api/v1/assets/
```

### Example Requests

#### Create Asset
```bash
POST /api/v1/assets/
Content-Type: application/json
Authorization: Bearer Jwt-access-token

{
    "name": "Apple Inc.",
    "symbol": "AAPL",
    "asset_type": "STOCK",
    "current_price": "150.25",
    "currency": "USD",
    "market_cap": "2400000000000",
    "description": "Technology company",
    "exchange": "NASDAQ",
    "risk_level": "MEDIUM"
}
```

#### Record Transaction
```bash
POST /api/v1/transactions/
Content-Type: application/json
Authorization: Bearer Jwt-access-token

{
    "asset": "asset_uuid_here",
    "transaction_type": "BUY",
    "quantity": "100",
    "price_per_unit": "150.25",
    "fees": "9.99",
    "order_type": "MARKET",
    "notes": "Monthly investment"
}
```

#### Get Dashboard Analytics
```bash
GET /api/v1/analytics/graphs/?days=30
Authorization: Bearer Jwt-access-token
```

## 🔧 Configuration

### Environment Variables
Key environment variables (see `.env.example`):

```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=asset_management
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### Database Configuration
The system uses SQLite by default. For development, you can use Postgresql:

```python
# In settings.py for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='asset_management'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test assets

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Test Coverage
The project includes comprehensive test coverage for:
- Model validation and business logic
- API endpoint functionality
- Permission and authentication
- Data integrity and constraints

## 🚀 Deployment

### Production Settings
1. Set `DEBUG = False`
2. Configure proper database settings
3. Set up static file serving
4. Configure email backend
5. Set secure cookies and HTTPS

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Environment-specific Settings
Create separate settings files (for more complex projects):
- `settings/development.py`
- `settings/production.py`
- `settings/testing.py`

## 📊 Performance Optimization

### Database Optimization
- Proper indexing on frequently queried fields
- Use of `select_related()` and `prefetch_related()`
- Database connection pooling
- Query optimization with `only()` and `defer()`

### Caching Strategy
```python
# Cache expensive calculations
from django.core.cache import cache

def get_portfolio_performance():
    cache_key = f"portfolio_performance_{user.id}"
    data = cache.get(cache_key)
    if not data:
        data = calculate_performance()
        cache.set(cache_key, data, 300)  # 5 minutes
    return data
```

### API Performance
- Pagination for large datasets
- Field selection for reduced payload
- Compression for API responses
- Rate limiting for API protection

## 🔒 Security Features

### Authentication & Authorization
- JWT authentication
- Role-based access control
- Object-level permissions
- User isolation for data access

### Data Protection
- Input validation and sanitization
- SQL injection prevention (Django ORM)
- XSS protection
- CSRF protection
- Secure headers configuration

### API Security
- Rate limiting
- Request size limits
- CORS configuration
- HTTPS enforcement in production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- Follow PEP 8 guidelines
- Use Black for code formatting
- Add docstrings to all functions and classes
- Write comprehensive tests for new features

## 📝 Changelog

### Version 1.0.0
- Initial release with core functionality
- Asset management system
- Transaction recording
- Basic reporting
- Analytics dashboard
- API documentation

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Email: support@yourcompany.com
- Documentation: `/api/docs/`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ using Django REST Framework**
```

---

## Summary 

### 🔧 **Technical Implementation:**

1. **Models**:
   - comprehensive validation and business logic
   - Proper relationships and indexing
   - Soft delete functionality
   - Field validation with proper constraints

2. **Comprehensive Serializers**:
   - Multiple serializers for different use cases (list, detail, create)
   - Cross-field validation
   - Proper error handling and messaging
   - Performance optimizations

3. **Robust Views**:
   - Proper error handling and logging
   - Performance optimizations with select_related/prefetch_related
   - Enhanced filtering and search capabilities
   - Custom actions with proper documentation

4. **Security Enhancements**:
   - Custom permission classes
   - Proper object-level permissions
   - Input validation and sanitization
   - Rate limiting ready implementation

### 📚 **Documentation Improvements:**

1. **Comprehensive Swagger Documentation**:
   - Detailed endpoint descriptions
   - Request/response examples
   - Parameter documentation
   - Authentication guidance

2. **Code Documentation**:
   - Detailed docstrings for all functions
   - Inline comments for complex logic
   - Type hints where appropriate
   - Business logic explanations

3. **Setup Documentation**:
   - Complete installation guide
   - Configuration instructions
   - Environment setup
   - Deployment guidelines

### 🚀 **Best Practices Implemented:**

1. **Django/DRF Best Practices**:
   - Proper app structure
   - Separation of concerns
   - DRY principle implementation
   - Consistent naming conventions

2. **API Design**:
   - RESTful endpoint design
   - Consistent error responses
   - Proper HTTP status codes
   - Versioning support

3. **Performance**:
   - Database query optimization
   - Caching implementation
   - Pagination for large datasets
   - Efficient serialization

4. **Security**:
   - Authentication and authorization
   - Input validation
   - Error handling without information leakage
   - Security headers configuration


```

### Generate Mock Data:

```bash
# Basic generation
python manage.py generate_mock_data

# Custom amounts
python manage.py generate_mock_data --users 50 --assets 200 --transactions 1000

# Clear existing data and generate fresh
python manage.py generate_mock_data --clear --create-superuser

# Generate with specific verified user percentage
python manage.py generate_mock_data --verified-users 0.9
```
This comprehensive mock data generation system provides:

1. **Realistic Data**: Based on real stock symbols, prices, and market data
2. **Custom User Model Support**: Works with your OTP verification system
3. **Comprehensive Coverage**: Users, profiles, assets, transactions, reports
4. **Flexible Configuration**: Customizable amounts and parameters
5. **Easy Setup**: One-command data generation

The system creates verified users (80% by default), realistic transactions, and comprehensive asset data that works perfectly with your custom User model and the analytics dashboard! 🚀

### login details
```bash
for admin user 

email: admin@example.com
password: admin1234

for normal user
email:joshua.white264@example.com
password: password123
```

### Note:
You cannot use the admin user to log in to the dashboard, or use the normal user to log in to the dashboard.
### Dashboard Access:
The Dashboard is restricted to the developer alone and is not accessible to normal users or admin users.