from backend.app import app, db
from backend.models import Product

with app.app_context():
    ref = Product.query.filter(Product.name.ilike('%refrigerator%')).first()
    if ref:
        # Extract the actual image URL from the Bing search link
        direct_url = "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6511/6511565cv18d.jpg"
        ref.image_url = direct_url
        db.session.commit()
        print(f"Updated Refrigerator image to: {direct_url}")
