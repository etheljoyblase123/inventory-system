import os
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import functools

app = Flask(__name__)
app.secret_key = 'super-secret-key-replace-me'
db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'inventory.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False, default='password')
    role = db.Column(db.String(50), default='User')
    avatar_seed = db.Column(db.String(100), default='Devoryn')
    is_admin = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default='Active')
    last_login = db.Column(db.String(50))

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100))
    action = db.Column(db.String(200))
    time = db.Column(db.String(50))
    status = db.Column(db.String(20))

class DesignTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50))
    priority = db.Column(db.String(50))
    task = db.Column(db.String(255))
    assigned = db.Column(db.String(100))
    due = db.Column(db.String(50))

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100))
    text = db.Column(db.Text)
    time = db.Column(db.String(50))
    unread = db.Column(db.Boolean, default=False)

class ArchivedReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    date = db.Column(db.String(50))
    user = db.Column(db.String(100))
    format = db.Column(db.String(20))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(50))
    price = db.Column(db.Float, default=0.0)
    stock = db.Column(db.Integer, default=0)

class SupportRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(200))
    details = db.Column(db.Text)
    priority = db.Column(db.String(50))
    requested_by = db.Column(db.String(100))

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
            return redirect(url_for('user_dashboard'))
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
        Product(name="Nebula Workstation V1", sku="NB-WRK-001", category="Electronics", price=2499.0, stock=15),
        Product(name="Quantum Drive 2TB", sku="QD-SSD-012", category="Storage", price=189.0, stock=8),
        Product(name="Glass Core Logic Unit", sku="LU-GLS-045", category="Mainframe", price=4500.0, stock=2)
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
            user.last_login = datetime.now().strftime("%b %d, %H:%M %p")
            db.session.commit()
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        if User.query.filter_by(email=email).first():
            return "Email already exists"
        new_user = User(name=name, email=email, password=password, is_admin=False)
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
    stats = {"total_users": "124,500", "revenue": "$842,000", "active_sessions": "8,750"}
    activity = Activity.query.order_by(Activity.id.desc()).limit(10).all()
    tasks = DesignTask.query.all()
    messages_list = Message.query.all()
    return render_template('index.html', stats=stats, activity=activity, tasks=tasks, messages=messages_list)

# User dashboard removed - all users are admin

@app.route('/users')
@login_required
def users():
    users_list = User.query.all()
    messages_list = Message.query.all()
    return render_template('users.html', users=users_list, messages=messages_list)

@app.route('/analytics')
@login_required
def analytics():
    messages_list = Message.query.all()
    return render_template('analytics.html', messages=messages_list)

@app.route('/products')
@login_required
def products():
    prods = Product.query.all()
    messages_list = Message.query.all()
    return render_template('products.html', products=prods, messages=messages_list)

@app.route('/reports')
@login_required
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
        role=data.get('role', 'User'),
        status='Active',
        last_login=datetime.now().strftime("%b %d, %H:%M %p")
    )
    db.session.add(new_user)
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
    app.run(debug=True, port=5000)
