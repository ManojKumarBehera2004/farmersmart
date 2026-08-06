from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os
import random
import string
from datetime import datetime, timedelta
import requests
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Ensure instance and upload folders exist early
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
UPLOAD_DIR = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(INSTANCE_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Use absolute path for SQLite to avoid Windows cwd/path issues
DB_PATH = os.path.join(INSTANCE_DIR, 'farmers_mart.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Directories ensured above

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Twilio configuration (you'll need to add your credentials)
TWILIO_ACCOUNT_SID = 'your_twilio_account_sid'
TWILIO_AUTH_TOKEN = 'your_twilio_auth_token'
TWILIO_PHONE_NUMBER = 'your_twilio_phone_number'

# In-memory OTP storage (in production, use Redis or database)
otp_storage = {}

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'farmer' or 'consumer'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', backref='farmer', lazy=True)
    orders = db.relationship('Order', backref='consumer', lazy=True)
    cart_items = db.relationship('CartItem', backref='user', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    image_filename = db.Column(db.String(100), nullable=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    product = db.relationship('Product', backref='cart_items')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    consumer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, delivered
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    order_items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    product = db.relationship('Product', backref='order_items')

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='reviews')
    product = db.relationship('Product', backref='reviews')

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_otp(phone_number, otp):
    """Send OTP via Twilio SMS (placeholder implementation)"""
    # In a real implementation, you would use Twilio API
    # For now, we'll just print the OTP to console for testing
    print(f"OTP for {phone_number}: {otp}")
    return True

def get_weather_recommendation():
    """Mock function to get current weather and product recommendations"""
    # In a real app, this would call a Weather API
    weathers = [
        {'condition': 'Sunny', 'icon': 'fas fa-sun', 'keywords': ['mango', 'banana', 'coconut', 'juice']},
        {'condition': 'Rainy', 'icon': 'fas fa-cloud-rain', 'keywords': ['corn', 'tea', 'coffee', 'spices']},
        {'condition': 'Cold', 'icon': 'fas fa-snowflake', 'keywords': ['ginger', 'potato', 'honey']},
    ]
    current_weather = random.choice(weathers)
    return current_weather

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/send_otp', methods=['POST'])
def send_otp_route():
    data = request.get_json()
    phone_number = data.get('phone_number')
    
    if not phone_number:
        return jsonify({'success': False, 'message': 'Phone number is required'})
    
    # Generate and store OTP
    otp = generate_otp()
    otp_storage[phone_number] = {
        'otp': otp,
        'expires_at': datetime.utcnow() + timedelta(minutes=5)
    }
    
    # Send OTP
    if send_otp(phone_number, otp):
        # Improve logging for OTP debugging
        app.logger.info(f"OTP for {phone_number}: {otp}")
        print(f"OTP for {phone_number}: {otp}", flush=True)
        
        response = {'success': True, 'message': 'OTP sent successfully'}
        # Include OTP in response if in debug mode for easier testing
        if app.debug:
            response['debug_otp'] = otp
        return jsonify(response)
    else:
        return jsonify({'success': False, 'message': 'Failed to send OTP'})

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    phone_number = data.get('phone_number')
    otp = data.get('otp')
    user_type = data.get('user_type')
    name = data.get('name')
    
    if not all([phone_number, otp]):
        return jsonify({'success': False, 'message': 'Phone number and OTP are required'})
    
    # Check if OTP exists and is valid
    stored_otp_data = otp_storage.get(phone_number)
    if not stored_otp_data:
        return jsonify({'success': False, 'message': 'OTP not found'})
    
    if datetime.utcnow() > stored_otp_data['expires_at']:
        del otp_storage[phone_number]
        return jsonify({'success': False, 'message': 'OTP expired'})
    
    if stored_otp_data['otp'] != otp:
        return jsonify({'success': False, 'message': 'Invalid OTP'})
    
    # OTP verified, create or login user
    user = User.query.filter_by(phone_number=phone_number).first()
    
    if not user and name and user_type:
        # Register new user
        user = User(phone_number=phone_number, name=name, user_type=user_type)
        db.session.add(user)
        db.session.commit()
    
    if user:
        session['user_id'] = user.id
        session['user_type'] = user.user_type
        session['user_name'] = user.name
        
        # Clean up OTP
        del otp_storage[phone_number]
        
        # Redirect based on user type
        if user.user_type == 'farmer':
            redirect_url = url_for('farmer_dashboard')
        else:
            redirect_url = url_for('consumer_dashboard')
        
        return jsonify({'success': True, 'redirect': redirect_url})
    
    return jsonify({'success': False, 'message': 'User not found'})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/farmer_dashboard')
def farmer_dashboard():
    if 'user_id' not in session or session.get('user_type') != 'farmer':
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    products = Product.query.filter_by(farmer_id=user.id).all()
    
    return render_template('farmer_dashboard.html', user=user, products=products)

@app.route('/consumer_dashboard')
def consumer_dashboard():
    if 'user_id' not in session or session.get('user_type') != 'consumer':
        return redirect(url_for('login'))
    
    products = Product.query.filter_by(is_active=True).all()
    
    # Get weather recommendations
    weather = get_weather_recommendation()
    recommended_products = []
    
    # Simple recommendation logic based on name matching keywords
    for p in products:
        for keyword in weather['keywords']:
            if keyword.lower() in p.name.lower() or keyword.lower() in p.description.lower():
                recommended_products.append(p)
                break
    
    return render_template('consumer_dashboard.html', 
                           products=products, 
                           weather=weather, 
                           recommended_products=recommended_products)

@app.route('/marketplace')
def marketplace():
    search_query = request.args.get('search', '')
    products = Product.query.filter_by(is_active=True)
    
    if search_query:
        # Search across name + description (case-insensitive)
        like = f"%{search_query}%"
        products = products.filter(
            db.or_(
                Product.name.ilike(like),
                Product.description.ilike(like)
            )
        )
    
    products = products.all()
    return render_template('marketplace.html', products=products, search_query=search_query)

@app.route('/add_product', methods=['POST'])
def add_product():
    if 'user_id' not in session or session.get('user_type') != 'farmer':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        name = request.form.get('name')
        price = float(request.form.get('price'))
        quantity = int(request.form.get('quantity'))
        description = request.form.get('description')
        
        if not all([name, price, quantity, description]):
            return jsonify({'success': False, 'message': 'All fields are required'})
        
        # Handle image upload
        image_filename = None
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and image_file.filename:
                filename = secure_filename(image_file.filename)
                # Add timestamp to avoid filename conflicts
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_')
                image_filename = timestamp + filename
                image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        
        product = Product(
            name=name,
            price=price,
            quantity=quantity,
            description=description,
            image_filename=image_filename,
            farmer_id=session['user_id']
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Product added successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/get_product/<int:product_id>')
def get_product(product_id):
    if 'user_id' not in session or session.get('user_type') != 'farmer':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    product = Product.query.filter_by(id=product_id, farmer_id=session['user_id']).first()
    if not product:
        return jsonify({'success': False, 'message': 'Product not found'})
    
    return jsonify({
        'id': product.id,
        'name': product.name,
        'price': product.price,
        'quantity': product.quantity,
        'description': product.description,
        'is_active': product.is_active
    })

@app.route('/edit_product/<int:product_id>', methods=['POST'])
def edit_product(product_id):
    if 'user_id' not in session or session.get('user_type') != 'farmer':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        product = Product.query.filter_by(id=product_id, farmer_id=session['user_id']).first()
        if not product:
            return jsonify({'success': False, 'message': 'Product not found'})
        
        product.name = request.form.get('name')
        product.price = float(request.form.get('price'))
        product.quantity = int(request.form.get('quantity'))
        product.description = request.form.get('description')
        product.is_active = request.form.get('is_active') == 'true'
        
        # Handle image upload
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and image_file.filename:
                # Delete old image if exists
                if product.image_filename:
                    old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], product.image_filename)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                
                filename = secure_filename(image_file.filename)
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_')
                product.image_filename = timestamp + filename
                image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], product.image_filename))
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Product updated successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/delete_product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    if 'user_id' not in session or session.get('user_type') != 'farmer':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        product = Product.query.filter_by(id=product_id, farmer_id=session['user_id']).first()
        if not product:
            return jsonify({'success': False, 'message': 'Product not found'})
        
        # Delete image file if exists
        if product.image_filename:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], product.image_filename)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Product deleted successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/get_product_details/<int:product_id>')
def get_product_details(product_id):
    product = Product.query.filter_by(id=product_id, is_active=True).first()
    if not product:
        return jsonify({'success': False, 'message': 'Product not found'})
    
    # Calculate average rating
    reviews = Review.query.filter_by(product_id=product_id).all()
    avg_rating = 0
    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
    
    reviews_data = [{
        'user_name': r.user.name,
        'rating': r.rating,
        'comment': r.comment,
        'created_at': r.created_at.strftime('%d %b %Y')
    } for r in reviews]
    
    return jsonify({
        'id': product.id,
        'name': product.name,
        'price': product.price,
        'quantity': product.quantity,
        'description': product.description,
        'image_filename': product.image_filename,
        'farmer_name': product.farmer.name,
        'created_at': product.created_at.isoformat(),
        'avg_rating': round(avg_rating, 1),
        'review_count': len(reviews),
        'reviews': reviews_data
    })

@app.route('/submit_review', methods=['POST'])
def submit_review():
    if 'user_id' not in session or session.get('user_type') != 'consumer':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        rating_raw = data.get('rating')
        comment = data.get('comment')
        
        if not product_id:
            return jsonify({'success': False, 'message': 'Product is required'})

        if rating_raw is None or str(rating_raw).strip() == '':
            return jsonify({'success': False, 'message': 'Rating is required'})

        try:
            rating = int(rating_raw)
        except (TypeError, ValueError):
            return jsonify({'success': False, 'message': 'Rating must be a number'})

        if rating < 1 or rating > 5:
            return jsonify({'success': False, 'message': 'Rating must be between 1 and 5'})

        product = Product.query.filter_by(id=product_id, is_active=True).first()
        if not product:
            return jsonify({'success': False, 'message': 'Product not found'})
        
        # Check if user already reviewed this product? (Optional, let's allow multiple for now or restrict)
        # For simple MVP, we just add it.
        
        review = Review(
            product_id=product_id,
            user_id=session['user_id'],
            rating=rating,
            comment=comment
        )
        
        db.session.add(review)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Review submitted successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/checkout')
def checkout():
    if 'user_id' not in session or session.get('user_type') != 'consumer':
        return redirect(url_for('login'))
    
    return render_template('checkout.html')

@app.route('/create_order', methods=['POST'])
def create_order():
    if 'user_id' not in session or session.get('user_type') != 'consumer':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        data = request.get_json()
        cart_items = data.get('cart_items', [])
        
        if not cart_items:
            return jsonify({'success': False, 'message': 'Cart is empty'})
        
        total_amount = 0
        order_items = []
        
        # Validate cart items and calculate total
        for item in cart_items:
            product = Product.query.filter_by(id=item['id'], is_active=True).first()
            if not product:
                return jsonify({'success': False, 'message': f'Product {item["name"]} not found'})
            
            if product.quantity < item['quantity']:
                return jsonify({'success': False, 'message': f'Insufficient quantity for {product.name}'})
            
            item_total = product.price * item['quantity']
            total_amount += item_total
            
            order_items.append({
                'product': product,
                'quantity': item['quantity'],
                'price': product.price
            })
        
        # Create order
        order = Order(
            consumer_id=session['user_id'],
            total_amount=total_amount,
            status='pending',
            payment_status='pending'
        )
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Create order items and update product quantities
        for item in order_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['product'].id,
                quantity=item['quantity'],
                price=item['price']
            )
            db.session.add(order_item)
            
            # Update product quantity
            item['product'].quantity -= item['quantity']
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'order_id': order.id,
            'total_amount': total_amount,
            'message': 'Order created successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/payment/<int:order_id>')
def payment(order_id):
    if 'user_id' not in session or session.get('user_type') != 'consumer':
        return redirect(url_for('login'))
    
    order = Order.query.filter_by(id=order_id, consumer_id=session['user_id']).first()
    if not order:
        flash('Order not found', 'error')
        return redirect(url_for('consumer_dashboard'))
    
    return render_template('payment.html', order=order)

@app.route('/confirm_payment', methods=['POST'])
def confirm_payment():
    if 'user_id' not in session or session.get('user_type') != 'consumer':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        
        order = Order.query.filter_by(id=order_id, consumer_id=session['user_id']).first()
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'})
        
        # Update order status (in real implementation, verify payment first)
        order.payment_status = 'paid'
        order.status = 'confirmed'
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Payment confirmed successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/orders')
def orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if user.user_type == 'consumer':
        orders = Order.query.filter_by(consumer_id=user.id).order_by(Order.created_at.desc()).all()
        return render_template('consumer_orders.html', orders=orders)
    else:
        # For farmers, show orders for their products
        farmer_orders = db.session.query(Order).join(OrderItem).join(Product).filter(
            Product.farmer_id == user.id
        ).distinct().order_by(Order.created_at.desc()).all()
        return render_template('farmer_orders.html', orders=farmer_orders)

@app.route('/update_order_status', methods=['POST'])
def update_order_status():
    if 'user_id' not in session or session.get('user_type') != 'farmer':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        new_status = data.get('status')
        
        # Verify farmer owns products in this order
        order = db.session.query(Order).join(OrderItem).join(Product).filter(
            Order.id == order_id,
            Product.farmer_id == session['user_id']
        ).first()
        
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'})
        
        order.status = new_status
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Order status updated successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
