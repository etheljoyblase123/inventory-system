from backend.app import app, db, seed_db
with app.app_context():
    db.drop_all()
    db.create_all()
    seed_db()
    print("Database reset and seeded!")
