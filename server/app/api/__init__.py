from flask import Blueprint

api = Blueprint("api", __name__)

from app.api import auth


@api.get("/health")
def health():
    return {"status": "ok"}, 200


from app.api.products import products_bp
from app.api.categories import categories_bp
from app.api.stock_movements import stock_movements_bp


def register_resource_blueprints(app):
    app.register_blueprint(products_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(stock_movements_bp)


