from app.extensions import db


class QuoteItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    quote_id = db.Column(
        db.Integer,
        db.ForeignKey("quote.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id"),
        nullable=False
    )

    quantity = db.Column(db.Integer, nullable=False)

    unit_price = db.Column(db.Numeric(10, 2), nullable=False)

    quote = db.relationship("Quote", back_populates="items")
    product = db.relationship("Product", back_populates="quote_items")

    @property
    def line_total(self):
        return self.quantity * self.unit_price

    def __repr__(self):
        return (
            f"<QuoteItem {self.id}: "
            f"Quote {self.quote_id}, Product {self.product_id}, "
            f"Quantity {self.quantity}>"
        )