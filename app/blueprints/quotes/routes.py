from decimal import Decimal

from flask import redirect, render_template, request, url_for
from flask_login import login_required

from app.blueprints.quotes import quotes_bp
from app.extensions import db
from app.models import Customer, Product, Quote, QuoteItem


@quotes_bp.route("/")
@login_required
def quote_list():
    quotes = (
        db.session.execute(
            db.select(Quote).order_by(Quote.created_at.desc())
        )
        .scalars()
        .all()
    )

    return render_template(
        "quotes/list.html",
        quotes=quotes
    )


@quotes_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_quote():
    customers = (
        db.session.execute(
            db.select(Customer).order_by(
                Customer.first_name,
                Customer.last_name
            )
        )
        .scalars()
        .all()
    )

    active_products = (
        db.session.execute(
            db.select(Product)
            .where(Product.is_active.is_(True))
            .order_by(
                Product.category,
                Product.brand,
                Product.model
            )
        )
        .scalars()
        .all()
    )

    errors = []

    if request.method == "POST":
        customer_id = request.form.get("customer_id", type=int)
        system_size_text = request.form.get("system_size", "").strip()
        battery_size_text = request.form.get("battery_size", "").strip()

        customer = (
            db.session.get(Customer, customer_id)
            if customer_id is not None
            else None
        )

        if customer is None:
            errors.append("Please select a valid customer.")

        try:
            system_size = float(system_size_text)

            if system_size <= 0:
                errors.append("System size must be greater than 0.")
        except ValueError:
            system_size = None
            errors.append("Please enter a valid system size.")

        if battery_size_text:
            try:
                battery_size = float(battery_size_text)

                if battery_size < 0:
                    errors.append(
                        "Battery size cannot be negative."
                    )
            except ValueError:
                battery_size = None
                errors.append(
                    "Please enter a valid battery size."
                )
        else:
            battery_size = None

        selected_items = []

        for product in active_products:
            quantity_text = request.form.get(
                f"quantity_{product.id}",
                ""
            ).strip()

            if not quantity_text:
                continue

            try:
                quantity = int(quantity_text)
            except ValueError:
                errors.append(
                    f"Quantity for {product.brand} "
                    f"{product.model} must be a whole number."
                )
                continue

            if quantity < 0:
                errors.append(
                    f"Quantity for {product.brand} "
                    f"{product.model} cannot be negative."
                )
                continue

            if quantity > 0:
                selected_items.append(
                    (product, quantity)
                )

        if not selected_items:
            errors.append(
                "Please add at least one product to the quote."
            )

        if not errors:
            quote = Quote(
                customer_id=customer.id,
                system_size=system_size,
                battery_size=battery_size,
                status="draft",
                total_price=Decimal("0.00")
            )

            db.session.add(quote)
            db.session.flush()

            quote_total = Decimal("0.00")

            for product, quantity in selected_items:
                item = QuoteItem(
                    quote_id=quote.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=product.unit_price
                )

                db.session.add(item)

                quote_total += item.line_total

            quote.total_price = quote_total

            db.session.commit()

            return redirect(
                url_for(
                    "quotes.quote_detail",
                    quote_id=quote.id
                )
            )

    return render_template(
        "quotes/create.html",
        customers=customers,
        products=active_products,
        errors=errors,
        form_data=request.form
    )


@quotes_bp.route("/<int:quote_id>/edit", methods=["GET", "POST"])
@login_required
def edit_quote(quote_id):
    quote = db.get_or_404(Quote, quote_id)

    customers = (
        db.session.execute(
            db.select(Customer).order_by(
                Customer.first_name,
                Customer.last_name
            )
        )
        .scalars()
        .all()
    )

    existing_items = {
        item.product_id: item
        for item in quote.items
    }

    active_products = (
        db.session.execute(
            db.select(Product)
            .where(Product.is_active.is_(True))
            .order_by(
                Product.category,
                Product.brand,
                Product.model
            )
        )
        .scalars()
        .all()
    )

    products_by_id = {
        product.id: product
        for product in active_products
    }

    for item in quote.items:
        products_by_id[item.product.id] = item.product

    products = sorted(
        products_by_id.values(),
        key=lambda product: (
            product.category,
            product.brand,
            product.model
        )
    )

    errors = []

    if request.method == "POST":
        customer_id = request.form.get("customer_id", type=int)
        system_size_text = request.form.get("system_size", "").strip()
        battery_size_text = request.form.get("battery_size", "").strip()
        status = request.form.get("status", "").strip()

        customer = (
            db.session.get(Customer, customer_id)
            if customer_id is not None
            else None
        )

        if customer is None:
            errors.append("Please select a valid customer.")

        try:
            system_size = float(system_size_text)

            if system_size <= 0:
                errors.append("System size must be greater than 0.")
        except ValueError:
            system_size = None
            errors.append("Please enter a valid system size.")

        if battery_size_text:
            try:
                battery_size = float(battery_size_text)

                if battery_size < 0:
                    errors.append(
                        "Battery size cannot be negative."
                    )
            except ValueError:
                battery_size = None
                errors.append(
                    "Please enter a valid battery size."
                )
        else:
            battery_size = None

        valid_statuses = {
            "draft",
            "sent",
            "accepted",
            "rejected"
        }

        if status not in valid_statuses:
            errors.append("Please select a valid quote status.")

        quantities = {}

        for product in products:
            quantity_text = request.form.get(
                f"quantity_{product.id}",
                ""
            ).strip()

            if not quantity_text:
                quantity = 0
            else:
                try:
                    quantity = int(quantity_text)
                except ValueError:
                    errors.append(
                        f"Quantity for {product.brand} "
                        f"{product.model} must be a whole number."
                    )
                    continue

            if quantity < 0:
                errors.append(
                    f"Quantity for {product.brand} "
                    f"{product.model} cannot be negative."
                )
                continue

            quantities[product.id] = quantity

        if not any(
            quantity > 0
            for quantity in quantities.values()
        ):
            errors.append(
                "A quote must contain at least one product."
            )

        if not errors:
            quote.customer_id = customer.id
            quote.system_size = system_size
            quote.battery_size = battery_size
            quote.status = status

            for product in products:
                quantity = quantities.get(product.id, 0)
                existing_item = existing_items.get(product.id)

                if existing_item and quantity > 0:
                    existing_item.quantity = quantity

                elif existing_item and quantity == 0:
                    db.session.delete(existing_item)

                elif not existing_item and quantity > 0:
                    new_item = QuoteItem(
                        quote_id=quote.id,
                        product_id=product.id,
                        quantity=quantity,
                        unit_price=product.unit_price
                    )

                    db.session.add(new_item)

            db.session.flush()

            quote.total_price = sum(
                (
                    item.line_total
                    for item in quote.items
                    if item not in db.session.deleted
                ),
                Decimal("0.00")
            )

            db.session.commit()

            return redirect(
                url_for(
                    "quotes.quote_detail",
                    quote_id=quote.id
                )
            )

    return render_template(
        "quotes/edit.html",
        quote=quote,
        customers=customers,
        products=products,
        existing_items=existing_items,
        errors=errors,
        form_data=request.form
    )


@quotes_bp.route("/<int:quote_id>")
@login_required
def quote_detail(quote_id):
    quote = db.get_or_404(Quote, quote_id)

    return render_template(
        "quotes/detail.html",
        quote=quote
    )