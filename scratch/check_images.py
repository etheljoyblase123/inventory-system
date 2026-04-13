from backend.app import app, db
from backend.models import Product

with app.app_context():
    products = Product.query.all()
    for p in products:
        print(f"ID: {p.id}, Name: {p.name}, Image: {p.image_url}")
