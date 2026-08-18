from flask import abort, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from app.blueprints.customers import customers_bp
from app.extensions import db
from app.models.customer import Customer


@customers_bp.route("/")
def customer_list():
    customers = db.session.execute(
        db.select(Customer).order_by(Customer.id)
    ).scalars().all()

    return render_template(
        "customers/list.html",
        customers=customers
    )


@customers_bp.route("/<int:customer_id>")
def customer_detail(customer_id):
    customer = db.session.get(Customer, customer_id)

    if customer is None:
        abort(404)

    delete_error = request.args.get("delete_error")

    return render_template(
        "customers/detail.html",
        customer=customer,
        delete_error=delete_error
    )


@customers_bp.route("/create", methods=["GET", "POST"])
def customer_create():
    error = None

    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()

        if not first_name:
            error = "First name is required."
        elif not last_name:
            error = "Last name is required."
        elif not email:
            error = "Email is required."
        elif not phone:
            error = "Phone is required."
        else:
            customer = Customer(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone
            )

            db.session.add(customer)

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                error = "A customer with this email already exists."
            else:
                return redirect(
                    url_for(
                        "customers.customer_detail",
                        customer_id=customer.id
                    )
                )

    return render_template(
        "customers/create.html",
        error=error
    )
@customers_bp.route("/<int:customer_id>/edit", methods=["GET", "POST"])
def customer_edit(customer_id):
    customer = db.session.get(Customer, customer_id)

    if customer is None:
        abort(404)

    error = None

    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()

        if not first_name:
            error = "First name is required."
        elif not last_name:
            error = "Last name is required."
        elif not email:
            error = "Email is required."
        elif not phone:
            error = "Phone is required."
        else:
            customer.first_name = first_name
            customer.last_name = last_name
            customer.email = email
            customer.phone = phone

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                error = "A customer with this email already exists."
            else:
                return redirect(
                    url_for(
                        "customers.customer_detail",
                        customer_id=customer.id
                    )
                )

    return render_template(
        "customers/edit.html",
        customer=customer,
        error=error
    )
@customers_bp.route("/<int:customer_id>/delete", methods=["POST"])
def customer_delete(customer_id):
    customer = db.session.get(Customer, customer_id)

    if customer is None:
        abort(404)

    if customer.quotes:
        return redirect(
            url_for(
                "customers.customer_detail",
                customer_id=customer.id,
                delete_error="quotes"
            )
        )

    db.session.delete(customer)
    db.session.commit()

    return redirect(
        url_for("customers.customer_list")
    )