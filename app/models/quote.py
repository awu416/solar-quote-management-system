from app.extensions import db


class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customer.id"),
        nullable=False
    )
    system_size = db.Column(db.Float, nullable=False)
    battery_size = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="draft")
    total_price = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    
    customer = db.relationship("Customer", back_populates="quotes")
    
    def __repr__(self):
        return f"<Quote {self.id}: {self.system_size} kW - {self.status}>"