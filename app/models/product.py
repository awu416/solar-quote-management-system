from app.extensions import db


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)

    unit_price = db.Column(db.Numeric(10, 2), nullable=False)

    is_active = db.Column(db.Boolean, nullable=False, default=True)

    quote_items = db.relationship(
        "QuoteItem",
        back_populates="product"
    )

    def __repr__(self):
        return f"<Product {self.brand} {self.model}>"