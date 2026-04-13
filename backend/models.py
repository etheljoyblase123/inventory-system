from backend.extensions import db
from datetime import datetime

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

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "avatar_seed": self.avatar_seed,
            "is_admin": self.is_admin,
            "status": self.status,
            "last_login": self.last_login
        }

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
    rating = db.Column(db.Float, default=0.0)
    image_url = db.Column(db.String(500))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "sku": self.sku,
            "category": self.category,
            "price": self.price,
            "stock": self.stock,
            "rating": self.rating,
            "image_url": self.image_url
        }

class SupportRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(200))
    details = db.Column(db.Text)
    priority = db.Column(db.String(50))
    requested_by = db.Column(db.String(100))

# Buyer Models
class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PurchaseOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    status = db.Column(db.String(20), default='Draft') # Draft, Pending, Received
    total_amount = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    received_at = db.Column(db.DateTime)
    
    supplier = db.relationship('Supplier', backref=db.backref('purchase_orders', lazy=True))

class PurchaseOrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False)

    po = db.relationship('PurchaseOrder', backref=db.backref('items', lazy=True))
    product = db.relationship('Product', backref=db.backref('po_items', lazy=True))

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, default=1)
    amount = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', backref=db.backref('sales', lazy=True))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default='Pending') # Pending, Confirmed, Cancelled
    total_amount = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('orders', lazy=True))

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float)

    order = db.relationship('Order', backref=db.backref('items', lazy=True))
    product = db.relationship('Product')
