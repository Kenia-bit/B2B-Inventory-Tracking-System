from flask import Flask, jsonify, request, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Farmer, Harvest, Buyer, Order

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

import os

# Get the database URL from Render environment variables, or fall back to local sqlite
db_url = os.environ.get("DATABASE_URL", "sqlite:///app.db")

# Render gives "postgres://...", but SQLAlchemy requires "postgresql://..."
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

with app.app_context():
    db.create_all()

# --- AUTH ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        
        return render_template('login.html', error="Invalid email or password")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            return render_template('signup.html', error="Email already exists")
            
        hashed_pw = generate_password_hash(password, method='scrypt')
        new_user = User(email=email, full_name=full_name, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- PROTECTED APP ROUTE ---

@app.route('/', methods=['GET'])
@login_required
def home():
    return render_template('index.html', current_user=current_user)

# --- USER-SCOPED API ENDPOINTS ---

@app.route('/api/farmers', methods=['GET'])
@login_required
def get_farmers():
    farmers = Farmer.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        "farmer_id": f.farmer_id,
        "full_name": f.full_name,
        "phone_number": f.phone_number,
        "location": f.location,
        "created_at": f.created_at.strftime("%Y-%m-%d %H:%M") if f.created_at else "N/A"
    } for f in farmers])

@app.route('/api/farmers', methods=['POST'])
@login_required
def add_farmer():
    data = request.get_json()
    new_farmer = Farmer(
        full_name=data['full_name'],
        phone_number=data.get('phone_number'),
        location=data.get('location'),
        user_id=current_user.id
    )
    db.session.add(new_farmer)
    db.session.commit()
    return jsonify({"message": "Farmer registered successfully!"}), 201

# --- DELETE FARMER ROUTE ---
@app.route('/api/farmers/<int:farmer_id>', methods=['DELETE'])
@login_required
def delete_farmer(farmer_id):
    farmer = Farmer.query.filter_by(id=farmer_id, user_id=current_user.id).first_or_404()
    
    # A must check: prevent deletion if farmer has active harvest logs
    has_harvests = Harvest.query.filter_by(farmer_id=farmer_id).first()
    if has_harvests:
        return jsonify({'error': 'Cannot delete farmer with recorded harvests.'}), 400

    db.session.delete(farmer)
    db.session.commit()
    return jsonify({'message': 'Farmer deleted successfully!'}), 200


@app.route('/api/harvests', methods=['GET'])
@login_required
def get_harvests():
    harvests = Harvest.query.filter_by(user_id=current_user.id).all()
    results = []
    for h in harvests:
        # Fetch associated farmer name safely
        farmer = db.session.get(Farmer, h.farmer_id) if h.farmer_id else None
        results.append({
            'id': h.harvest_id,
            'crop_type': h.crop_type,
            'quantity_kg': h.quantity_kg,
            'harvest_date': h.harvest_date.strftime('%Y-%m-%d') if h.harvest_date else '',
            'farmer_name': farmer.full_name if farmer else 'Unknown Farmer'
        })
    return jsonify(results)

# Add Toggle Status Route for Orders
@app.route('/api/orders/<int:order_id>/toggle-status', methods=['PATCH', 'POST'])
@login_required
def toggle_order_status(order_id):
    order = Order.query.filter_by(order_id=order_id, user_id=current_user.id).first_or_404()
    
    # Toggle between PAID and DEBT
    if order.payment_status.upper() == 'DEBT':
        order.payment_status = 'PAID'
    else:
        order.payment_status = 'DEBT'
        
    db.session.commit()
    return jsonify({'success': True, 'new_status': order.payment_status})


@app.route('/api/harvests', methods=['POST'])
@login_required
def add_harvest():
    data = request.get_json()
    new_h = Harvest(
        farmer_id=data['farmer_id'],
        crop_type=data['crop_type'],
        quantity_kg=data['quantity_kg'],
        harvest_date=data['harvest_date'],
        user_id=current_user.id
    )
    db.session.add(new_h)
    db.session.commit()
    return jsonify({"message": "Harvest logged successfully!"}), 201

# --- BUYERS & ORDERS APIs ---

@app.route('/api/buyers', methods=['GET', 'POST'])
@login_required
def handle_buyers():
    if request.method == 'POST':
        data = request.json
        email = data.get('email', '').strip().lower()
        full_name = data.get('full_name', '').strip()

        # Check for existing duplicate buyer under this user
        existing_buyer = Buyer.query.filter_by(user_id=current_user.id, email=email).first()
        if existing_buyer and email:
            return jsonify({'error': f'Buyer with email {email} already exists!'}), 400

        new_buyer = Buyer(
            user_id=current_user.id,
            full_name=full_name,
            phone_number=data.get('phone_number'),
            email=email,
            location=data.get('location')
        )
        db.session.add(new_buyer)
        db.session.commit()
        return jsonify({'message': 'Buyer registered successfully!'}), 201

    buyers = Buyer.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': b.buyer_id,
        'full_name': b.full_name,
        'phone_number': b.phone_number,
        'email': b.email,  # Ensure email is included
        'location': b.location
    } for b in buyers])


# --- ORDER & DEBT ROUTES ---
@app.route('/api/orders', methods=['GET', 'POST'])
@login_required
def handle_orders():
    if request.method == 'POST':
        data = request.get_json()

        # Parse form inputs safely
        harvest_id = int(data['harvest_id'])
        buyer_id = int(data['buyer_id'])
        qty = float(data['quantity_kg'])
        unit_price = float(data.get('unit_price', 0))
        
        # Calculate total price if not provided
        total_price = float(data.get('total_price', qty * unit_price))
        payment_status = data.get('payment_status', 'debt')

        # 1. Fetch harvest object from DB to validate stock
        harvest = db.session.get(Harvest, harvest_id)
        if not harvest or harvest.user_id != current_user.id:
            return jsonify({"error": "Invalid harvest batch selected"}), 400

        # 2. Check if enough stock exists
        if float(harvest.quantity_kg) < qty:
            return jsonify({"error": f"Only {harvest.quantity_kg}kg available in stock!"}), 400

        # 3. Deduct stock from harvest batch
        harvest.quantity_kg = float(harvest.quantity_kg) - qty

        # 4. Save new order
        new_order = Order(
            user_id=current_user.id,
            buyer_id=buyer_id,
            harvest_id=harvest_id,
            quantity_kg=qty,
            unit_price=unit_price,
            total_price=total_price,
            payment_status=payment_status
        )
        db.session.add(new_order)
        db.session.commit()
        return jsonify({"message": "Order recorded successfully!"}), 201

    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.order_date.desc()).all()
    return jsonify([{
        "order_id": o.order_id,
        "buyer_name": o.buyer.full_name if o.buyer else "N/A",
        "crop_type": o.harvest.crop_type if o.harvest else "N/A",
        "quantity_kg": float(o.quantity_kg),
        "unit_price": float(o.unit_price) if o.unit_price else 0.0,
        "total_price": float(o.total_price),
        "payment_status": o.payment_status,
        "order_date": o.order_date.strftime("%Y-%m-%d %H:%M") if o.order_date else "N/A"
    } for o in orders])


# --- FORGOT / RESET PASSWORD ROUTE ---

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        user = User.query.filter_by(email=email).first()

        if not user:
            return render_template('reset_password.html', error="No account found with that email address.")

        if new_password != confirm_password:
            return render_template('reset_password.html', error="Passwords do not match.", email=email)

        # Hash new password and update user record
        user.password = generate_password_hash(new_password, method='scrypt')
        db.session.commit()

        flash("Password updated successfully! You can now log in.")
        return redirect(url_for('login'))

    return render_template('reset_password.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)