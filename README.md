# FARMERS MART - Complete Full-Stack Web Application

A comprehensive farmers marketplace web application built with Python Flask, featuring farmer and consumer dashboards, product management, cart functionality, and UPI payment integration.

## Features

### 🌱 For Farmers
- **Registration & Authentication**: Mobile OTP-based secure registration
- **Product Management**: Add, edit, delete products with image uploads
- **Dashboard**: View product statistics and manage inventory
- **Order Management**: Track customer orders and update order status
- **Earnings Tracking**: Monitor sales and revenue

### 🛒 For Consumers
- **Registration & Authentication**: Mobile OTP-based secure registration
- **Product Browsing**: Search, filter, and sort products
- **Shopping Cart**: Add products to cart with quantity management
- **Secure Checkout**: UPI-based payment system
- **Order History**: Track order status and payment history

### 🔧 Technical Features
- **Responsive Design**: Bootstrap-powered modern UI
- **Image Upload**: Secure product image storage
- **Session Management**: Secure user authentication
- **Database**: SQLite with SQLAlchemy ORM
- **Mobile OTP**: Twilio integration for phone verification
- **UPI Payment**: Integrated payment system with QR codes

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### 1. Clone/Download the Project
```bash
cd "d:\Farmer shop"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Twilio (Optional)
For SMS OTP functionality, update the following in `app.py`:
```python
TWILIO_ACCOUNT_SID = 'your_twilio_account_sid'
TWILIO_AUTH_TOKEN = 'your_twilio_auth_token'
TWILIO_PHONE_NUMBER = 'your_twilio_phone_number'
```

**Note**: The application works in demo mode without Twilio - OTPs are printed to console.

### 4. Run the Application
```bash
python app.py
```

The application will be available at: `http://localhost:5000`

## Project Structure

```
Farmer shop/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── farmers_mart.db                 # SQLite database (auto-created)
├── static/
│   └── uploads/                    # Product images storage
└── templates/
    ├── base.html                   # Base template
    ├── index.html                  # Homepage
    ├── register.html               # User registration
    ├── login.html                  # User login
    ├── farmer_dashboard.html       # Farmer dashboard
    ├── consumer_dashboard.html     # Consumer dashboard
    ├── marketplace.html            # Product marketplace
    ├── checkout.html               # Shopping cart checkout
    ├── payment.html                # UPI payment page
    ├── consumer_orders.html        # Consumer order history
    └── farmer_orders.html          # Farmer order management
```

## Database Models

### User
- ID, phone number, name, user type (farmer/consumer)
- Relationships to products, orders, and cart items

### Product
- ID, name, description, price, quantity, image
- Belongs to farmer, has order items and cart items

### Order & OrderItem
- Order tracking with status and payment information
- Individual items within each order

### CartItem
- Shopping cart functionality for consumers

## Usage Guide

### Getting Started

1. **Visit the Homepage**: Navigate to `http://localhost:5000`
2. **Register**: Click "Register" and choose farmer or consumer
3. **Verify Phone**: Enter your phone number and verify with OTP
4. **Complete Profile**: Fill in your name and user type

### For Farmers

1. **Access Dashboard**: Login and go to farmer dashboard
2. **Add Products**: Click "Add New Product" and fill details
3. **Upload Images**: Add product photos for better visibility
4. **Manage Inventory**: Edit quantities and product status
5. **Track Orders**: View customer orders and update status

### For Consumers

1. **Browse Products**: Visit marketplace or consumer dashboard
2. **Search & Filter**: Use search bar and sorting options
3. **Add to Cart**: Select products and quantities
4. **Checkout**: Review cart and proceed to payment
5. **Pay with UPI**: Use provided UPI ID or scan QR code
6. **Track Orders**: Monitor order status in order history

## Payment System

The application uses a UPI-based payment system:

- **UPI ID**: `trishulkumar6996@oksbi`
- **Payment Flow**: 
  1. Customer places order
  2. Redirected to payment page with UPI details
  3. Customer pays using any UPI app
  4. Manual confirmation updates order status
- **Security**: Orders are created only after cart validation

## API Endpoints

### Authentication
- `POST /send_otp` - Send OTP to phone number
- `POST /verify_otp` - Verify OTP and login/register
- `GET /logout` - Logout user

### Products (Farmers)
- `POST /add_product` - Add new product
- `GET /get_product/<id>` - Get product details
- `POST /edit_product/<id>` - Update product
- `DELETE /delete_product/<id>` - Delete product

### Shopping (Consumers)
- `GET /marketplace` - Browse all products
- `GET /get_product_details/<id>` - Get product details
- `POST /create_order` - Create order from cart
- `POST /confirm_payment` - Confirm payment

### Orders
- `GET /orders` - View order history
- `POST /update_order_status` - Update order status (farmers)

## Security Features

- **Session Management**: Secure user sessions
- **File Upload Security**: Secure filename handling
- **Input Validation**: Server-side validation for all inputs
- **Authentication**: Route protection based on user type
- **OTP Verification**: Mobile number verification

## Customization

### Styling
- Modify CSS variables in `templates/base.html`
- Bootstrap 5 classes for responsive design
- Custom color scheme with green theme

### Database
- SQLite for development (easily replaceable with PostgreSQL/MySQL)
- SQLAlchemy ORM for database operations

### Payment Integration
- Currently uses manual UPI confirmation
- Can be extended with payment gateway APIs

## Troubleshooting

### Common Issues

1. **Database Errors**: Delete `farmers_mart.db` to reset database
2. **Image Upload Issues**: Check `static/uploads/` directory permissions
3. **OTP Not Working**: Check Twilio configuration or use console output
4. **Port Conflicts**: Change port in `app.py` if 5000 is occupied

### Development Mode
- Debug mode is enabled by default
- Check console for detailed error messages
- Database is auto-created on first run

## Production Deployment

For production deployment:

1. **Disable Debug Mode**: Set `debug=False` in `app.py`
2. **Use Production Database**: Replace SQLite with PostgreSQL/MySQL
3. **Configure Twilio**: Add real Twilio credentials
4. **Secure Secret Key**: Use environment variables for secrets
5. **Use WSGI Server**: Deploy with Gunicorn or uWSGI
6. **Set Up SSL**: Use HTTPS for secure communication

## Contributing

This is a complete full-stack application ready for use. Key areas for enhancement:
- Real-time notifications
- Advanced search and filtering
- Payment gateway integration
- Mobile app development
- Analytics dashboard

## License

This project is created for educational and commercial use. Feel free to modify and distribute.

---

**FARMERS MART** - Connecting farmers directly with consumers for fresh, quality produce! 🌱🛒
