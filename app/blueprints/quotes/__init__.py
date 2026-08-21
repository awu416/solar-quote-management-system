from flask import Blueprint


quotes_bp = Blueprint(
    "quotes",
    __name__,
    url_prefix="/quotes"
)


from app.blueprints.quotes import routes