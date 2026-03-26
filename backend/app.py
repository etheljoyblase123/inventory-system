"""
Inventory Management System — Flask Backend
Admin-only | MariaDB via XAMPP | Jinja2 Templates
"""

from flask import Flask, request, render_template, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
import os

# Point Flask to the frontend/templates directory and frontend/static directory
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, '..', 'frontend', 'templates')
static_dir = os.path.join(base_dir, '..', 'frontend', 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = "inventory_secret_key"

# ─────────────────────────────────────────────
# Database Configuration (XAMPP MariaDB)
# ─────────────────────────────────────────────
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",       # Default XAMPP user
    "password": "",       # Default XAMPP password (empty)
    "database": "inventory_system",
}


def get_db():
    """Create and return a new database connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        raise RuntimeError(f"Database connection failed: {e}")


# ─────────────────────────────────────────────
# Products Routes
# ─────────────────────────────────────────────

@app.route("/products")
def products():
    """List all products."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products ORDER BY product_id")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("products.html", products=rows)


@app.route("/products/add", methods=["GET", "POST"])
def add_product():
    """Add a new product."""
    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        price    = request.form.get("price", "")
        stock    = request.form.get("stock", 0)
        min_stock = request.form.get("min_stock", 5)

        # Validation
        errors = []
        if not name:
            errors.append("Product name is required.")
        try:
            price = float(price)
            if price < 0:
                errors.append("Price cannot be negative.")
        except ValueError:
            errors.append("Price must be a valid number.")
        try:
            stock = int(stock)
            if stock < 0:
                errors.append("Stock cannot be negative.")
        except ValueError:
            errors.append("Stock must be a valid integer.")
        try:
            min_stock = int(min_stock)
            if min_stock < 0:
                errors.append("Minimum stock cannot be negative.")
        except ValueError:
            errors.append("Minimum stock must be a valid integer.")

        if errors:
            for e in errors:
                flash(e, "danger")
            conn2 = get_db()
            cur2 = conn2.cursor(dictionary=True)
            cur2.execute("SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND category != '' ORDER BY category")
            categories = [r['category'] for r in cur2.fetchall()]
            cur2.close()
            conn2.close()
            return render_template("add_product.html", categories=categories)


        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (name, category, price, stock, min_stock) VALUES (%s, %s, %s, %s, %s)",
            (name, category, price, stock, min_stock),
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash("Product added successfully!", "success")
        return redirect(url_for("products"))

    conn3 = get_db()
    cur3 = conn3.cursor(dictionary=True)
    cur3.execute("SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND category != '' ORDER BY category")
    categories = [r['category'] for r in cur3.fetchall()]
    cur3.close()
    conn3.close()
    return render_template("add_product.html", categories=categories)



@app.route("/products/update/<int:product_id>", methods=["GET", "POST"])
def update_product(product_id):
    """Update product details."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        name      = request.form.get("name", "").strip()
        category  = request.form.get("category", "").strip()
        price     = request.form.get("price", "")
        min_stock = request.form.get("min_stock", 5)

        errors = []
        if not name:
            errors.append("Product name is required.")
        try:
            price = float(price)
            if price < 0:
                errors.append("Price cannot be negative.")
        except ValueError:
            errors.append("Price must be a valid number.")
        try:
            min_stock = int(min_stock)
            if min_stock < 0:
                errors.append("Minimum stock cannot be negative.")
        except ValueError:
            errors.append("Minimum stock must be a valid integer.")

        if errors:
            for e in errors:
                flash(e, "danger")
            cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
            product = cursor.fetchone()
            cursor.close()
            conn.close()
            return render_template("add_product.html", product=product)

        cursor.execute(
            "UPDATE products SET name=%s, category=%s, price=%s, min_stock=%s WHERE product_id=%s",
            (name, category, price, min_stock, product_id),
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash("Product updated successfully!", "success")
        return redirect(url_for("products"))

    # GET — load existing product for editing
    cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
    product = cursor.fetchone()
    cursor.execute("SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND category != '' ORDER BY category")
    categories = [row['category'] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("products"))
    return render_template("add_product.html", product=product, categories=categories)



# ─────────────────────────────────────────────
# Sales Routes
# ─────────────────────────────────────────────

@app.route("/sales")
def sales():
    """List all sales with their items."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.sale_id, s.total_amount, s.created_at,
               GROUP_CONCAT(p.name ORDER BY p.name SEPARATOR ', ') AS product_names
        FROM sales s
        LEFT JOIN sale_items si ON s.sale_id = si.sale_id
        LEFT JOIN products p   ON si.product_id = p.product_id
        GROUP BY s.sale_id
        ORDER BY s.created_at DESC
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("sales.html", sales=rows)


@app.route("/sales/add", methods=["GET", "POST"])
def add_sale():
    """Record a new sale — updates stock and logs stock_movements."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        product_ids = request.form.getlist("product_id")
        quantities  = request.form.getlist("quantity")

        if not product_ids:
            flash("At least one product must be selected.", "danger")
            cursor.execute("SELECT * FROM products WHERE stock > 0 ORDER BY name")
            available = cursor.fetchall()
            cursor.close()
            conn.close()
            return render_template("add_sale.html", products=available)

        errors = []
        items = []
        total = 0.0

        for pid, qty in zip(product_ids, quantities):
            if not pid:
                continue
            try:
                qty = int(qty)
                if qty <= 0:
                    errors.append(f"Quantity for product #{pid} must be positive.")
                    continue
            except ValueError:
                errors.append(f"Invalid quantity for product #{pid}.")
                continue

            cursor.execute("SELECT * FROM products WHERE product_id = %s", (pid,))
            product = cursor.fetchone()
            if not product:
                errors.append(f"Product #{pid} not found.")
                continue
            if product["stock"] < qty:
                errors.append(
                    f"Insufficient stock for '{product['name']}'. Available: {product['stock']}."
                )
                continue

            items.append({"product": product, "qty": qty})
            total += float(product["price"]) * qty

        if errors:
            for e in errors:
                flash(e, "danger")
            cursor.execute("SELECT * FROM products WHERE stock > 0 ORDER BY name")
            available = cursor.fetchall()
            cursor.close()
            conn.close()
            return render_template("add_sale.html", products=available)

        # Insert sale record
        cursor2 = conn.cursor()
        cursor2.execute("INSERT INTO sales (total_amount) VALUES (%s)", (round(total, 2),))
        sale_id = cursor2.lastrowid

        for item in items:
            p   = item["product"]
            qty = item["qty"]
            # Insert sale item
            cursor2.execute(
                "INSERT INTO sale_items (sale_id, product_id, quantity, price) VALUES (%s,%s,%s,%s)",
                (sale_id, p["product_id"], qty, p["price"]),
            )
            # Deduct stock
            cursor2.execute(
                "UPDATE products SET stock = stock - %s WHERE product_id = %s",
                (qty, p["product_id"]),
            )
            # Log movement
            cursor2.execute(
                "INSERT INTO stock_movements (product_id, type, quantity, reason) VALUES (%s,'OUT',%s,%s)",
                (p["product_id"], qty, f"Sale #{sale_id}"),
            )

        conn.commit()
        cursor.close()
        cursor2.close()
        conn.close()
        flash(f"Sale #{sale_id} recorded. Total: ₱{total:.2f}", "success")
        return redirect(url_for("sales"))

    # GET — load available products
    cursor.execute("SELECT * FROM products WHERE stock > 0 ORDER BY name")
    available = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("add_sale.html", products=available)


# ─────────────────────────────────────────────
# Stock Routes
# ─────────────────────────────────────────────

@app.route("/stock/in", methods=["GET", "POST"])
def stock_in():
    """Add stock for a product (Stock IN)."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        product_id = request.form.get("product_id")
        quantity   = request.form.get("quantity", "")
        reason     = request.form.get("reason", "").strip()

        errors = []
        try:
            quantity = int(quantity)
            if quantity <= 0:
                errors.append("Quantity must be a positive integer.")
        except ValueError:
            errors.append("Quantity must be a valid integer.")

        if errors:
            for e in errors:
                flash(e, "danger")
            cursor.execute("SELECT * FROM products ORDER BY name")
            products = cursor.fetchall()
            cursor.close()
            conn.close()
            return render_template("stock.html", products=products, action="in")

        cursor2 = conn.cursor()
        cursor2.execute(
            "UPDATE products SET stock = stock + %s WHERE product_id = %s",
            (quantity, product_id),
        )
        cursor2.execute(
            "INSERT INTO stock_movements (product_id, type, quantity, reason) VALUES (%s,'IN',%s,%s)",
            (product_id, quantity, reason or "Stock replenishment"),
        )
        conn.commit()
        cursor.close()
        cursor2.close()
        conn.close()
        flash("Stock added successfully!", "success")
        return redirect(url_for("stock_in"))

    cursor.execute("SELECT * FROM products ORDER BY name")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("stock.html", products=products, action="in")


@app.route("/stock/out", methods=["GET", "POST"])
def stock_out():
    """Remove stock for a product (Stock OUT)."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        product_id = request.form.get("product_id")
        quantity   = request.form.get("quantity", "")
        reason     = request.form.get("reason", "").strip()

        errors = []
        try:
            quantity = int(quantity)
            if quantity <= 0:
                errors.append("Quantity must be a positive integer.")
        except ValueError:
            errors.append("Quantity must be a valid integer.")

        if not errors:
            cursor.execute("SELECT stock, name FROM products WHERE product_id = %s", (product_id,))
            product = cursor.fetchone()
            if not product:
                errors.append("Product not found.")
            elif product["stock"] < quantity:
                errors.append(
                    f"Cannot remove {quantity} units. Current stock for '{product['name']}': {product['stock']}."
                )

        if errors:
            for e in errors:
                flash(e, "danger")
            cursor.execute("SELECT * FROM products ORDER BY name")
            products = cursor.fetchall()
            cursor.close()
            conn.close()
            return render_template("stock.html", products=products, action="out")

        cursor2 = conn.cursor()
        cursor2.execute(
            "UPDATE products SET stock = stock - %s WHERE product_id = %s",
            (quantity, product_id),
        )
        cursor2.execute(
            "INSERT INTO stock_movements (product_id, type, quantity, reason) VALUES (%s,'OUT',%s,%s)",
            (product_id, quantity, reason or "Manual stock removal"),
        )
        conn.commit()
        cursor.close()
        cursor2.close()
        conn.close()
        flash("Stock removed successfully!", "success")
        return redirect(url_for("stock_out"))

    cursor.execute("SELECT * FROM products ORDER BY name")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("stock.html", products=products, action="out")


# ─────────────────────────────────────────────
# Reports Routes
# ─────────────────────────────────────────────

@app.route("/reports/fast-moving")
def report_fast_moving():
    """Show most sold products (by total quantity sold)."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.product_id, p.name, p.category, p.price, p.stock, p.min_stock,
               COALESCE(SUM(si.quantity), 0) AS total_sold
        FROM products p
        LEFT JOIN sale_items si ON p.product_id = si.product_id
        GROUP BY p.product_id
        ORDER BY total_sold DESC
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("reports.html", title="Fast-Moving Products", products=rows, report_type="fast")


@app.route("/reports/slow-moving")
def report_slow_moving():
    """Show least sold products (by total quantity sold)."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.product_id, p.name, p.category, p.price, p.stock, p.min_stock,
               COALESCE(SUM(si.quantity), 0) AS total_sold
        FROM products p
        LEFT JOIN sale_items si ON p.product_id = si.product_id
        GROUP BY p.product_id
        ORDER BY total_sold ASC
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("reports.html", title="Slow-Moving Products", products=rows, report_type="slow")


@app.route("/reports/low-stock")
def report_low_stock():
    """Show products where stock < min_stock."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM products
        WHERE stock < min_stock
        ORDER BY stock ASC
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("reports.html", title="Low-Stock Products", products=rows, report_type="low")


# ─────────────────────────────────────────────
# Dashboard & Root Route
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    """Main dashboard with summary metrics and recent activity."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Total Products
    cursor.execute("SELECT COUNT(*) as count FROM products")
    total_products = cursor.fetchone()["count"]
    
    # 2. Low Stock Count
    cursor.execute("SELECT COUNT(*) as count FROM products WHERE stock < min_stock")
    low_stock = cursor.fetchone()["count"]
    
    # 3. Today's Sales Count & Revenue
    cursor.execute("""
        SELECT COUNT(*) as sales_today, COALESCE(SUM(total_amount), 0) as revenue_today
        FROM sales 
        WHERE DATE(created_at) = CURDATE()
    """)
    today_stats = cursor.fetchone()
    
    # 4. Recent 5 Sales
    cursor.execute("""
        SELECT s.sale_id, s.total_amount, s.created_at,
               GROUP_CONCAT(p.name ORDER BY p.name SEPARATOR ', ') AS product_names
        FROM sales s
        LEFT JOIN sale_items si ON s.sale_id = si.sale_id
        LEFT JOIN products p   ON si.product_id = p.product_id
        GROUP BY s.sale_id
        ORDER BY s.created_at DESC
        LIMIT 5
    """)
    recent_sales = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template(
        "dashboard.html", 
        total_products=total_products,
        low_stock=low_stock,
        sales_today=today_stats["sales_today"],
        revenue_today=today_stats["revenue_today"],
        recent_sales=recent_sales
    )


# ─────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)
