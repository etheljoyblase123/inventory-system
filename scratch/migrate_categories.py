from backend.app import app, db
from backend.models import Product

with app.app_context():
    # Update products
    updated = Product.query.filter_by(category='Gadgets').update({'category': 'Office Supplies'})
    db.session.commit()
    print(f"Migrated {updated} products from Gadgets to Office Supplies.")
