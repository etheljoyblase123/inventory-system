import functools
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, flash
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
from models import User, Product, Activity, Supplier, PurchaseOrder, PurchaseOrderItem

buyer_bp = Blueprint('buyer', __name__, template_folder='templates')

def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@buyer_bp.route('/')
@login_required
def dashboard():
    search_query = request.args.get('search', '')
    if search_query:
        # Search by PO ID or Supplier Name
        pos = PurchaseOrder.query.join(Supplier).filter(
            (PurchaseOrder.id.like(f"%{search_query}%")) | 
            (Supplier.name.like(f"%{search_query}%"))
        ).all()
    else:
        pos = PurchaseOrder.query.order_by(PurchaseOrder.id.desc()).limit(20).all()
    
    return render_template('buyer/dashboard.html', pos=pos, search_query=search_query)

@buyer_bp.route('/draft/create', methods=['GET', 'POST'])
@login_required
def create_po():
    if request.method == 'POST':
        supplier_id = request.form.get('supplier_id')
        product_ids = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')
        
        if not supplier_id or not product_ids:
            return "Missing supplier or products", 400
            
        try:
            new_po = PurchaseOrder(supplier_id=supplier_id, status='Draft')
            db.session.add(new_po)
            db.session.flush() # Get PO ID
            
            total = 0
            for pid, qty in zip(product_ids, quantities):
                product = db.session.get(Product, pid)
                if product and int(qty) > 0:
                    item_total = float(qty) * product.price
                    po_item = PurchaseOrderItem(
                        po_id=new_po.id,
                        product_id=pid,
                        quantity=int(qty),
                        price_at_purchase=product.price
                    )
                    db.session.add(po_item)
                    total += item_total
            
            new_po.total_amount = total
            db.session.commit()
            return redirect(url_for('buyer.dashboard'))
        except SQLAlchemyError as e:
            db.session.rollback()
            return f"Error creating PO: {str(e)}", 500

    suppliers = Supplier.query.all()
    products = Product.query.all()
    return render_template('buyer/create_po.html', suppliers=suppliers, products=products)

@buyer_bp.route('/send/<int:po_id>', methods=['POST'])
@login_required
def send_po(po_id):
    po = db.session.get(PurchaseOrder, po_id)
    if po and po.status == 'Draft':
        po.status = 'Pending'
        db.session.commit()
    return redirect(url_for('buyer.dashboard'))

@buyer_bp.route('/pending')
@login_required
def pending_orders():
    pos = PurchaseOrder.query.filter_by(status='Pending').all()
    return render_template('buyer/pending.html', pos=pos)

@buyer_bp.route('/history')
@login_required
def history():
    pos = PurchaseOrder.query.filter_by(status='Received').all()
    return render_template('buyer/history.html', pos=pos)

@buyer_bp.route('/receive/<int:po_id>', methods=['POST'])
@login_required
def receive_po(po_id):
    po = db.session.get(PurchaseOrder, po_id)
    if not po or po.status != 'Pending':
        return jsonify({"success": False, "error": "Invalid PO or status"})

    try:
        # Use a transaction for stock update and status change
        with db.session.begin_nested():
            for item in po.items:
                product = db.session.get(Product, item.product_id)
                if not product:
                    raise Exception(f"Product {item.product_id} not found")
                
                # Update stock
                product.stock += item.quantity
            
            # Update PO status
            po.status = 'Received'
            po.received_at = datetime.utcnow()
            
            # Log activity
            new_activity = Activity(
                user_name=session.get('user_name', 'System'),
                action=f"Received PO #{po.id} from {po.supplier.name}",
                time=datetime.now().strftime("%b %d, %H:%M %p"),
                status="Completed"
            )
            db.session.add(new_activity)

        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)})
