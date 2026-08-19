from decimal import Decimal, InvalidOperation

from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.extensions import db
from app.models import Product
from app.blueprints.products import products_bp


VALID_CATEGORIES = {
    "panel",
    "inverter",
    "battery",
}


@products_bp.route("/")
@login_required
def list_products():
    products = db.session.execute(
        db.select(Product).order_by(Product.brand, Product.model)
    ).scalars().all()

    return render_template(
        "products/list.html",
        products=products
    )


@products_bp.route("/<int:product_id>")
@login_required
def product_detail(product_id):
    product = db.get_or_404(Product, product_id)

    return render_template(
        "products/detail.html",
        product=product
    )


@products_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_product():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        brand = request.form.get("brand", "").strip()
        model = request.form.get("model", "").strip()
        unit_price_input = request.form.get("unit_price", "").strip()

        errors = []

        if not name:
            errors.append("Name is required.")

        if category not in VALID_CATEGORIES:
            errors.append("Please select a valid category.")

        if not brand:
            errors.append("Brand is required.")

        if not model:
            errors.append("Model is required.")

        try:
            unit_price = Decimal(unit_price_input)

            if unit_price < 0:
                errors.append("Unit price cannot be negative.")

        except (InvalidOperation, ValueError):
            unit_price = None
            errors.append("Unit price must be a valid number.")

        if errors:
            return render_template(
                "products/create.html",
                errors=errors,
                form_data=request.form
            )

        product = Product(
            name=name,
            category=category,
            brand=brand,
            model=model,
            unit_price=unit_price
        )

        try:
            db.session.add(product)
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        flash("Product created successfully.")

        return redirect(
            url_for(
                "products.product_detail",
                product_id=product.id
            )
        )

    return render_template("products/create.html")


@products_bp.route("/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    product = db.get_or_404(Product, product_id)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        brand = request.form.get("brand", "").strip()
        model = request.form.get("model", "").strip()
        unit_price_input = request.form.get("unit_price", "").strip()

        errors = []

        if not name:
            errors.append("Name is required.")

        if category not in VALID_CATEGORIES:
            errors.append("Please select a valid category.")

        if not brand:
            errors.append("Brand is required.")

        if not model:
            errors.append("Model is required.")

        try:
            unit_price = Decimal(unit_price_input)

            if unit_price < 0:
                errors.append("Unit price cannot be negative.")

        except (InvalidOperation, ValueError):
            unit_price = None
            errors.append("Unit price must be a valid number.")

        if errors:
            return render_template(
                "products/edit.html",
                product=product,
                errors=errors,
                form_data=request.form
            )

        product.name = name
        product.category = category
        product.brand = brand
        product.model = model
        product.unit_price = unit_price

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        flash("Product updated successfully.")

        return redirect(
            url_for(
                "products.product_detail",
                product_id=product.id
            )
        )

    return render_template(
        "products/edit.html",
        product=product
    )

@products_bp.route("/<int:product_id>/deactivate", methods=["POST"])
@login_required
def deactivate_product(product_id):
    product = db.get_or_404(Product, product_id)

    product.is_active = False

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    flash("Product deactivated successfully.")

    return redirect(
        url_for(
            "products.product_detail",
            product_id=product.id
        )
    )


@products_bp.route("/<int:product_id>/activate", methods=["POST"])
@login_required
def activate_product(product_id):
    product = db.get_or_404(Product, product_id)

    product.is_active = True

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    flash("Product activated successfully.")

    return redirect(
        url_for(
            "products.product_detail",
            product_id=product.id
        )
    )    