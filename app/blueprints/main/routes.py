from flask import render_template
from flask_login import current_user

from app.blueprints.main import main_bp
from app.models import Customer, Product, Quote


@main_bp.route("/")
def home():
    if not current_user.is_authenticated:
        return render_template("main/index.html")

    total_customers = Customer.query.count()
    total_products = Product.query.count()
    total_quotes = Quote.query.count()
    accepted_quotes = Quote.query.filter_by(status="accepted").count()

    recent_quotes = (
        Quote.query
        .order_by(Quote.created_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "main/index.html",
        total_customers=total_customers,
        total_products=total_products,
        total_quotes=total_quotes,
        accepted_quotes=accepted_quotes,
        recent_quotes=recent_quotes,
    )