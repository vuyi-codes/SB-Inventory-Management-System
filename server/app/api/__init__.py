from flask import Blueprint

api = Blueprint("api", __name__)

from app.api import auth

from app.api.sales import sales_bp

from app.api.reports import reports_bp

@api.get("/health")
def health():
    return {"status": "ok"}, 200

api.register_blueprint(sales_bp)

api.register_blueprint(reports_bp)