import os
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from extensions import db
from models import User, Product, Activity, DesignTask, Message, ArchivedReport, Supplier, PurchaseOrder, PurchaseOrderItem, SupportRequest
from datetime import datetime
import functools

app = Flask(__name__)
app.secret_key = 'super-secret-key-replace-me'
db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'inventory.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)

# Helper Decorators
def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        user = db.session.get(User, session.get('user_id'))
        if not user or not user.is_admin:
            return redirect(url_for('shop'))
        return f(*args, **kwargs)
    return decorated_function

# seeding function
def seed_db():
    if User.query.filter_by(email="devoryn@gmail.com").first(): return
    
    # initial users
    users = [
        User(name="Devoryn", email="devoryn@gmail.com", password="password", role="Admin", is_admin=True, status="Active", last_login="Oct 26, 10:15 AM", avatar_seed="Devoryn"),
        User(name="Alex M.", email="alex.m@gmail.com", password="password", role="Editor", is_admin=False, status="Active", last_login="Oct 26, 09:45 AM", avatar_seed="Alex"),
        User(name="Sarah K.", email="sarah.k@gmail.com", password="password", role="User", is_admin=False, status="Active", last_login="Oct 26, 08:00 AM", avatar_seed="Sarah")
    ]
    db.session.add_all(users)
    
    # initial products
    products = [
        Product(name="Product1", sku="NB-WRK-001", category="Electronics", price=2499.0, stock=15, rating=4.8),
        Product(name="product2", sku="QD-SSD-012", category="Storage", price=189.0, stock=8, rating=4.5),
        Product(name="product3", sku="LU-GLS-045", category="Mainframe", price=4500.0, stock=2, rating=5.0),
        Product(name="product4", sku="AZ-HDP-001", category="Accessories", price=349.0, stock=25, rating=4.7),
        Product(name="product5", sku="CW-WCH-002", category="Gadgets", price=199.0, stock=50, rating=4.2),
        Product(name="product6", sku="TM-KBD-003", category="Peripherals", price=159.0, stock=40, rating=4.6),
        Product(name="product7", sku="VP-MON-004", category="Electronics", price=899.0, stock=12, rating=4.9),
        Product(name="product8", sku="NC-PAD-005", category="Gadgets", price=49.0, stock=100, rating=4.0),
        Product(name="product9", sku="ES-SND-006", category="Audio", price=279.0, stock=30, rating=4.3),
        Product(name="product10", sku="PF-FIT-007", category="Gadgets", price=89.0, stock=4, rating=4.1),
        Product(name="product11", sku="SM-MSG-008", category="Peripherals", price=79.0, stock=60, rating=4.5),
        Product(name="product12", sku="VG-CHR-009", category="Furniture", price=399.0, stock=10, rating=4.8)
    ]
    db.session.add_all(products)
    
    # initial activity
    activities = [
        Activity(user_name="Devoryn", action="Updated system settings", time="Oct 26, 10:15 AM", status="Completed"),
        Activity(user_name="Alex M.", action="Generated sales report", time="Oct 26, 09:45 AM", status="Pending")
    ]
    db.session.add_all(activities)
    
    # initial tasks
    tasks = [
        DesignTask(status="IN_PROGRESS", priority="HIGH", task="Iterate Mobile Profile Screen", assigned="Devoryn", due="Oct 30"),
        DesignTask(status="REVIEW", priority="MED", task="Finalize Color System Guide", assigned="Sarah K.", due="Nov 1")
    ]
    db.session.add_all(tasks)
    
    # initial messages
    msgs = [
        Message(user="Sarah K.", text="Hi Devoryn, have you seen the report on the increased API error rate?", time="8:18 AM", unread=True),
        Message(user="Alex M.", text="Generated sales report", time="9:12 AM", unread=False)
    ]
    db.session.add_all(msgs)
    
    db.session.commit()

# Supplier Seeding
def seed_suppliers():
    if Supplier.query.first(): return
    suppliers = [
        Supplier(name="Nebula Tech Corp", email="contact@nebula.com", phone="123-456-7890", address="Silicon Valley, CA"),
        Supplier(name="Quantum Supplies", email="info@quantum.com", phone="987-654-3210", address="New York, NY"),
        Supplier(name="Global Mainframe", email="sales@global.com", phone="555-555-5555", address="London, UK")
    ]
    db.session.add_all(suppliers)
    db.session.commit()

# Main Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['role'] = user.role
            user.last_login = datetime.now().strftime("%b %d, %H:%M %p")
            db.session.commit()
            if user.is_admin:
                return redirect(url_for('index'))
            else:
                return redirect(url_for('shop'))
    return render_template('login.html')

@app.route('/shop')
@login_required
def shop():
    search_query = request.args.get('search', '')
    if search_query:
        prods = Product.query.filter(
            (Product.name.contains(search_query)) | 
            (Product.category.contains(search_query))
        ).all()
    else:
        prods = Product.query.all()
    return render_template('shop/home.html', products=prods, search_query=search_query)

@app.route('/shop/cart')
@login_required
def cart():
    return render_template('shop/cart.html')

@app.route('/shop/orders')
@login_required
def orders():
    return render_template('shop/orders.html')

@app.route('/shop/others')
@app.route('/shop/others/<tab>')
@login_required
def others(tab='profile'):
    return render_template('shop/others.html', active_tab=tab)

@app.route('/register', methods=['GET', 'POST'])
def register():
    # ... existing register code ...
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        if User.query.filter_by(email=email).first():
            return "Email already exists"
        
        role = request.form.get('role', 'Buyer')
        is_admin = (role == 'Admin')
        
        new_user = User(name=name, email=email, password=password, role=role, is_admin=is_admin)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    user = db.session.get(User, session.get('user_id'))
    if user and user.is_admin:
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('shop'))

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    stats = {"total_users": "124,500", "revenue": "$842,000", "active_sessions": "8,750"}
    activity = Activity.query.order_by(Activity.id.desc()).limit(10).all()
    tasks = DesignTask.query.all()
    messages_list = Message.query.all()
    return render_template('index.html', stats=stats, activity=activity, tasks=tasks, messages=messages_list)

# User dashboard removed - all users are admin

@app.route('/users')
@login_required
@admin_required
def users():
    search_query = request.args.get('search', '')
    if search_query:
        users_list = User.query.filter(
            (User.name.like(f"%{search_query}%")) | 
            (User.email.like(f"%{search_query}%"))
        ).all()
    else:
        users_list = User.query.all()
    messages_list = Message.query.all()
    return render_template('users.html', users=users_list, messages=messages_list, search_query=search_query)

@app.route('/analytics')
@login_required
@admin_required
def analytics():
    messages_list = Message.query.all()
    return render_template('analytics.html', messages=messages_list)

@app.route('/products')
@login_required
@admin_required
def products():
    search_query = request.args.get('search', '')
    if search_query:
        prods = Product.query.filter(
            (Product.name.like(f"%{search_query}%")) | 
            (Product.sku.like(f"%{search_query}%")) |
            (Product.category.like(f"%{search_query}%"))
        ).all()
    else:
        prods = Product.query.all()
    messages_list = Message.query.all()
    return render_template('products.html', products=prods, messages=messages_list, search_query=search_query)

@app.route('/reports')
@login_required
@admin_required
def reports():
    archived = ArchivedReport.query.all()
    messages_list = Message.query.all()
    scheduled = [{"name": "Weekly Stats", "freq": "Mon 9 AM", "next": "Oct 28", "recipient": "Admin"}]
    return render_template('reports.html', archived=archived, scheduled=scheduled, messages=messages_list)

# Form Endpoints (POST)
@app.route('/api/update-profile', methods=['POST'])
@login_required
def update_profile():
    user = db.session.get(User, session['user_id'])
    data = request.form
    user.name = data.get('name', user.name)
    user.avatar_seed = data.get('avatar_seed', user.avatar_seed)
    db.session.commit()
    session['user_name'] = user.name
    return jsonify({"success": True})

@app.route('/api/create-user', methods=['POST'])
@login_required
def create_user():
    data = request.form
    new_user = User(
        name=data.get('name', 'New'),
        email=data.get('email', ''),
        password=data.get('password', 'password'),
        role=data.get('role', 'User'),
        status='Active',
        last_login=datetime.now().strftime("%b %d, %H:%M %p"),
        is_admin=(data.get('role') == 'Admin')
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/delete-user/<int:id>', methods=['POST', 'DELETE'])
@login_required
@admin_required
def delete_user(id):
    user = db.session.get(User, id)
    if not user:
        return jsonify({"success": False, "error": "User not found"})
    if user.id == session.get('user_id'):
        return jsonify({"success": False, "error": "Cannot delete yourself"})
    db.session.delete(user)
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/update-user/<int:id>', methods=['POST'])
@login_required
@admin_required
def update_user(id):
    user = db.session.get(User, id)
    if not user:
        return jsonify({"success": False, "error": "User not found"})
    data = request.form
    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    user.role = data.get('role', user.role)
    user.is_admin = (user.role == 'Admin')
    if data.get('password'):
        user.password = data.get('password')
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/buy-product', methods=['POST'])
@login_required
def buy_product():
    data = request.form
    prod_id = data.get('product_id')
    product = db.session.get(Product, prod_id)
    
    if not product:
        return jsonify({"success": False, "error": "Product not found"})
    
    if product.stock <= 0:
        return jsonify({"success": False, "error": "Product is out of stock"})
    
    # Process Purchase
    product.stock -= 1
    
    # Log Activity
    user = db.session.get(User, session['user_id'])
    new_activity = Activity(
        user_name=user.name,
        action=f"Purchased {product.name}",
        time=datetime.now().strftime("%b %d, %H:%M %p"),
        status="Completed"
    )
    
    db.session.add(new_activity)
    db.session.commit()
    
    return jsonify({"success": True})

@app.route('/api/add-product', methods=['POST'])
@login_required
def add_product():
    data = request.form
    new_prod = Product(
        name=data.get('name'),
        sku=data.get('sku'),
        category=data.get('category'),
        price=float(data.get('price', 0)),
        stock=int(data.get('stock', 0))
    )
    db.session.add(new_prod)
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/delete-product/<int:id>', methods=['POST', 'DELETE'])
@login_required
@admin_required
def delete_product(id):
    product = db.session.get(Product, id)
    if not product:
        return jsonify({"success": False, "error": "Product not found"})
    db.session.delete(product)
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/update-product/<int:id>', methods=['POST'])
@login_required
@admin_required
def update_product(id):
    product = db.session.get(Product, id)
    if not product:
        return jsonify({"success": False, "error": "Product not found"})
    data = request.form
    product.name = data.get('name', product.name)
    product.sku = data.get('sku', product.sku)
    product.category = data.get('category', product.category)
    product.price = float(data.get('price', product.price))
    product.stock = int(data.get('stock', product.stock))
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/submit-support', methods=['POST'])
def submit_support():
    data = request.form
    req = SupportRequest(
        topic=data.get('topic', ''),
        details=data.get('details', ''),
        priority=data.get('priority', 'Low'),
        requested_by='Devoryn'
    )
    db.session.add(req)
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/schedule-maintenance', methods=['POST'])
def schedule_maintenance():
    return jsonify({"success": True})

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    data = request.form
    new_report = ArchivedReport(
        name=f"{data.get('type')} Report",
        date=datetime.now().strftime("%b %d"),
        user='Devoryn',
        format=data.get('format')
    )
    db.session.add(new_report)
    db.session.commit()
    return jsonify({"success": True})

@app.context_processor
def inject_user():
    def get_user():
        if 'user_id' in session:
            return db.session.get(User, session['user_id'])
        return None
    return dict(get_user=get_user)

@app.route('/api/stats')
def get_stats():
    return jsonify({
        "monthly_users": [12000, 15000, 14000, 18000, 22000, 19000, 25000, 23000, 28000, 31000, 29000, 34000],
        "resource_usage": {
            "categories": ["Auth", "Database", "API", "CPU", "Unit", "URL", "Email", "SDK", "EDIT", "Other"],
            "cpu": [400, 500, 450, 600, 300, 400, 200, 550, 480, 350],
            "memory": [200, 300, 250, 400, 150, 200, 100, 350, 280, 250],
            "storage": [100, 200, 150, 250, 100, 150, 50, 200, 180, 150]
        }
    })


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_db()
        seed_suppliers()
    app.run(debug=True, port=5000)
