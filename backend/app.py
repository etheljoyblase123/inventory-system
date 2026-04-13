import os
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import sys
# Support direct execution
if __name__ == "__main__":
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.extensions import db
from backend.models import User, Product, Activity, DesignTask, Message, ArchivedReport, Supplier, PurchaseOrder, PurchaseOrderItem, SupportRequest, Sale, Order, OrderItem
from datetime import datetime
import functools

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
app.secret_key = 'super-secret-key-replace-me'
db_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database')), 'inventory.db')
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
            return redirect(url_for('products'))
        return f(*args, **kwargs)
    return decorated_function

# seeding function
def seed_db():
    if User.query.filter_by(email="devoryn@gmail.com").first(): return
    
    now = datetime.now()
    today_str = now.strftime("%b %d, %H:%M %p")
    today_short = now.strftime("%b %d")
    
    # initial users
    users = [
        User(name="Devoryn", email="devoryn@gmail.com", password="password", role="Admin", is_admin=True, status="Active", last_login=today_str, avatar_seed="Devoryn"),
        User(name="Alex M.", email="alex.m@gmail.com", password="password", role="Editor", is_admin=False, status="Active", last_login=today_str, avatar_seed="Alex"),
        User(name="Sarah K.", email="sarah.k@gmail.com", password="password", role="User", is_admin=False, status="Active", last_login=today_str, avatar_seed="Sarah")
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
        Activity(user_name="Devoryn", action="Updated system settings", time=today_str, status="Completed"),
        Activity(user_name="Alex M.", action="Generated sales report", time=today_str, status="Pending")
    ]
    db.session.add_all(activities)
    
    # initial tasks
    tasks = [
        DesignTask(status="IN_PROGRESS", priority="HIGH", task="Iterate Mobile Profile Screen", assigned="Devoryn", due=today_short),
        DesignTask(status="REVIEW", priority="MED", task="Finalize Color System Guide", assigned="Sarah K.", due=today_short)
    ]
    db.session.add_all(tasks)
    
    # initial messages
    msgs = [
        Message(user="Sarah K.", text="Hi Devoryn, have you seen the report on the increased API error rate?", time=now.strftime("%H:%M %p"), unread=True),
        Message(user="Alex M.", text="Generated sales report", time=now.strftime("%H:%M %p"), unread=False)
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
                return redirect(url_for('products'))
        else:
            # Handle invalid credentials (could add flashing here)
            return render_template('login.html', error="Invalid email or password")
            
    return render_template('login.html')

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
    return redirect(url_for('buyer_dashboard'))

@app.route('/buyer/dashboard')
@login_required
def buyer_dashboard():
    user = db.session.get(User, session['user_id'])
    my_orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).limit(5).all()
    featured = Product.query.order_by(Product.id.desc()).limit(4).all()
    messages_list = Message.query.all()
    return render_template('buyer_dashboard.html', orders=my_orders, featured=featured, messages=messages_list)

@app.route('/buyer/orders')
@login_required
def buyer_orders():
    user = db.session.get(User, session['user_id'])
    my_orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    messages_list = Message.query.all()
    return render_template('buyer_orders.html', orders=my_orders, messages=messages_list)

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    # Calculate real stats
    total_products = Product.query.count()
    low_stock_threshold = 10
    low_stock_count = Product.query.filter(Product.stock < low_stock_threshold).count()
    out_of_stock_count = Product.query.filter(Product.stock == 0).count()
    total_stock_value = db.session.query(db.func.sum(Product.price * Product.stock)).scalar() or 0
    
    stats = {
        "revenue": f"${total_stock_value:,.0f}", # Using inventory value as a proxy for 'Revenue' or 'Asset Value'
        "active_sessions": f"{total_products}", # Using total products count
        "low_stock": low_stock_count,
        "out_of_stock": out_of_stock_count
    }
    
    # Top Low Stock Items for Dashboard
    top_low_stock = Product.query.filter(Product.stock < low_stock_threshold).order_by(Product.stock.asc()).limit(5).all()
    
    # Category Distribution for Dashboard
    categories_query = db.session.query(Product.category, db.func.count(Product.id)).group_by(Product.category).all()
    cat_distribution = [{"name": c[0] or "Uncategorized", "count": c[1]} for c in categories_query]

    activity = Activity.query.order_by(Activity.id.desc()).limit(10).all()
    tasks = DesignTask.query.all()
    messages_list = Message.query.all()
    return render_template('index.html', stats=stats, activity=activity, tasks=tasks, messages=messages_list, low_stock_items=top_low_stock, categories=cat_distribution)

# User dashboard removed - all users are admin



@app.route('/analytics')
@login_required
@admin_required
def analytics():
    messages_list = Message.query.all()
    return render_template('analytics.html', messages=messages_list)

@app.route('/products')
@login_required
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
    scheduled = [{"name": "Weekly Stats", "freq": "Mon 9 AM", "next": "April 20", "recipient": "Admin"}]
    return render_template('reports.html', archived=archived, scheduled=scheduled, messages=messages_list)

@app.route('/orders')
@login_required
@admin_required
def orders():
    all_orders = Order.query.order_by(Order.created_at.desc()).all()
    messages_list = Message.query.all()
    return render_template('orders.html', orders=all_orders, messages=messages_list)

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

@app.route('/api/buy-product', methods=['POST'])
@login_required
def buy_product():
    prod_id = request.form.get('product_id')
    return checkout_single(prod_id)

@app.route('/api/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    prod_id = request.form.get('product_id')
    cart = session.get('cart', [])
    cart.append(prod_id)
    session['cart'] = cart
    return jsonify({"success": True, "count": len(cart)})

@app.route('/api/cart/get')
@login_required
def get_cart():
    cart_ids = session.get('cart', [])
    if not cart_ids:
        return jsonify({"success": True, "items": [], "total": 0})
    
    # Simple count of each product
    counts = {}
    for cid in cart_ids:
        counts[cid] = counts.get(cid, 0) + 1
    
    items = []
    total = 0
    for cid, qty in counts.items():
        p = db.session.get(Product, cid)
        if p:
            items.append({
                "id": p.id,
                "name": p.name,
                "price": p.price,
                "quantity": qty,
                "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?q=80&w=50"
            })
            total += p.price * qty
            
    return jsonify({"success": True, "items": items, "total": total})

@app.route('/api/cart/checkout', methods=['POST'])
@login_required
def checkout():
    cart_ids = session.get('cart', [])
    if not cart_ids:
        return jsonify({"success": False, "error": "Cart is empty"})
    
    counts = {}
    for cid in cart_ids:
        counts[cid] = counts.get(cid, 0) + 1
    
    # Create Order
    new_order = Order(
        user_id=session['user_id'],
        status='Pending',
        total_amount=0,
        created_at=datetime.now()
    )
    db.session.add(new_order)
    db.session.flush()
    
    final_total = 0
    for cid, qty in counts.items():
        p = db.session.get(Product, cid)
        if not p or p.stock < qty:
            db.session.rollback()
            return jsonify({"success": False, "error": f"Insufficient stock for {p.name if p else 'product'}"})
        
        # Deduct stock
        p.stock -= qty
        
        # Create Order Item
        item = OrderItem(order_id=new_order.id, product_id=p.id, quantity=qty, price=p.price)
        db.session.add(item)
        final_total += p.price * qty
        
        # Record Sale
        sale = Sale(product_id=p.id, quantity=qty, amount=p.price * qty, timestamp=datetime.now())
        db.session.add(sale)

    new_order.total_amount = final_total
    session['cart'] = []
    db.session.commit()
    return jsonify({"success": True})

def checkout_single(prod_id):
    product = db.session.get(Product, prod_id)
    if not product or product.stock <= 0:
        return jsonify({"success": False, "error": "Out of stock"})
    
    product.stock -= 1
    new_order = Order(user_id=session['user_id'], status='Pending', total_amount=product.price, created_at=datetime.now())
    db.session.add(new_order)
    db.session.flush()
    db.session.add(OrderItem(order_id=new_order.id, product_id=product.id, quantity=1, price=product.price))
    db.session.add(Sale(product_id=product.id, quantity=1, amount=product.price, timestamp=datetime.now()))
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
        stock=int(data.get('stock', 0)),
        image_url=data.get('image_url')
    )
    db.session.add(new_prod)
    
    # Log Activity
    user = db.session.get(User, session['user_id'])
    new_activity = Activity(
        user_name=user.name,
        action=f"Added product: {new_prod.name}",
        time=datetime.now().strftime("%b %d, %H:%M %p"),
        status="Completed"
    )
    db.session.add(new_activity)
    
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/delete-product/<int:id>', methods=['POST', 'DELETE'])
@login_required
@admin_required
def delete_product(id):
    product = db.session.get(Product, id)
    if not product:
        return jsonify({"success": False, "error": "Product not found"})
    
    product_name = product.name
    db.session.delete(product)
    
    # Log Activity
    user = db.session.get(User, session['user_id'])
    new_activity = Activity(
        user_name=user.name,
        action=f"Deleted product: {product_name}",
        time=datetime.now().strftime("%b %d, %H:%M %p"),
        status="Completed"
    )
    db.session.add(new_activity)
    
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
    product.image_url = data.get('image_url', product.image_url)
    
    # Log Activity
    user = db.session.get(User, session['user_id'])
    new_activity = Activity(
        user_name=user.name,
        action=f"Updated product: {product.name}",
        time=datetime.now().strftime("%b %d, %H:%M %p"),
        status="Completed"
    )
    db.session.add(new_activity)
    
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

@app.route('/api/confirm-order', methods=['POST'])
@login_required
@admin_required
def confirm_order():
    order_id = request.form.get('order_id')
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"success": False, "error": "Order not found"})
    
    if order.status != 'Pending':
        return jsonify({"success": False, "error": "Order already processed"})

    # Item stock and sales were already handled at checkout
    order.status = 'Confirmed'
    
    # Log Activity
    new_activity = Activity(
        user_name=session.get('user_name', 'System'),
        action=f"Confirmed Order #{order.id}",
        time=datetime.now().strftime("%b %d, %H:%M %p"),
        status="Completed"
    )
    db.session.add(new_activity)
    
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/cancel-order', methods=['POST'])
@login_required
@admin_required
def cancel_order():
    order_id = request.form.get('order_id')
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"success": False, "error": "Order not found"})
    
    if order.status == 'Cancelled':
        return jsonify({"success": False, "error": "Order already cancelled"})

    # RESTOCK items
    for item in order.items:
        item.product.stock += item.quantity
    
    order.status = 'Cancelled'
    
    # Log Activity
    new_activity = Activity(
        user_name=session.get('user_name', 'System'),
        action=f"Cancelled Order #{order.id} (Restocked)",
        time=datetime.now().strftime("%b %d, %H:%M %p"),
        status="Cancelled"
    )
    db.session.add(new_activity)
    
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/tasks/get')
@login_required
@admin_required
def get_tasks():
    tasks = DesignTask.query.order_by(DesignTask.id.desc()).all()
    return jsonify({
        "success": True, 
        "tasks": [{
            "id": t.id,
            "task": t.task,
            "status": t.status,
            "priority": t.priority,
            "due": t.due
        } for t in tasks]
    })

# Task Manager API
@app.route('/api/tasks/add', methods=['POST'])
@login_required
@admin_required
def add_task():
    data = request.form
    new_task = DesignTask(
        task=data.get('task'),
        priority=data.get('priority', 'Medium'),
        status='Pending',
        due=data.get('due', datetime.now().strftime("%b %d")),
        assigned=session.get('user_name')
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/tasks/toggle/<int:task_id>', methods=['POST'])
@login_required
@admin_required
def toggle_task(task_id):
    task = db.session.get(DesignTask, task_id)
    if task:
        task.status = 'Completed' if task.status == 'Pending' else 'Pending'
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Task not found"})

@app.route('/api/tasks/delete/<int:task_id>', methods=['POST'])
@login_required
@admin_required
def delete_task(task_id):
    task = db.session.get(DesignTask, task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Task not found"})

# File Manager API (Daily Order Reports)
@app.route('/api/file-manager/reports')
@login_required
@admin_required
def get_file_reports():
    # Group confirmed orders by date
    orders = Order.query.filter_by(status='Confirmed').all()
    reports = {}
    for o in orders:
        date_str = o.created_at.strftime("%Y-%m-%d")
        if date_str not in reports:
            reports[date_str] = {"date": date_str, "count": 0, "total": 0}
        reports[date_str]["count"] += 1
        reports[date_str]["total"] += o.total_amount
    
    return jsonify({"success": True, "reports": list(reports.values())})

@app.context_processor
def inject_user():
    def get_user():
        if 'user_id' in session:
            return db.session.get(User, session['user_id'])
        return None
    return dict(get_user=get_user)

@app.route('/api/stats')
@login_required
@admin_required
def get_stats():
    # Real Inventory Stats
    low_stock_threshold = 10
    total_products = Product.query.count()
    low_stock_prods = Product.query.filter(Product.stock < low_stock_threshold).all()
    
    # Category Data
    categories_query = db.session.query(Product.category, db.func.count(Product.id), db.func.sum(Product.stock)).group_by(Product.category).all()
    cat_names = [c[0] or "Uncategorized" for c in categories_query]
    cat_counts = [c[1] for c in categories_query]
    cat_stock = [c[2] for c in categories_query]
    
    # Top Low Stock Items
    top_low_stock = [{"name": p.name, "stock": p.stock} for p in sorted(low_stock_prods, key=lambda x: x.stock)[:10]]
    
    # Sales Data (Real-time from Sale model)
    sales_data = db.session.query(
        db.func.strftime('%m', Sale.timestamp),
        db.func.sum(Sale.amount)
    ).group_by(db.func.strftime('%m', Sale.timestamp)).all()
    
    monthly_revenue = [0] * 12
    for m, val in sales_data:
        try:
            monthly_revenue[int(m)-1] = float(val)
        except: pass

    return jsonify({
        "inventory_summary": {
            "total_products": total_products,
            "low_stock_count": len(low_stock_prods),
            "categories_count": len(cat_names)
        },
        "category_distribution": {
            "labels": cat_names,
            "counts": cat_counts,
            "stock_levels": cat_stock
        },
        "low_stock_items": top_low_stock,
        "monthly_revenue": monthly_revenue
    })


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_db()
        seed_suppliers()
    app.run(debug=True, port=5000)
