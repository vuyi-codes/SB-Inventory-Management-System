from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.extensions import db
from app.models import Category, Product, SaleItem, PurchaseOrderItem

products_bp = Blueprint("products", __name__)


def product_json(product):
    return {
        "id": product.id,
        "sku": product.sku,
        "name": product.name,
        "description": product.description,
        "category_id": product.category_id,
        "category_name": product.category.name if product.category else None,
        "cost_price": format(product.cost_price, ".2f"),
        "selling_price": format(product.selling_price, ".2f"),
        "quantity": product.quantity,
        "reorder_level": product.reorder_level,
        "is_active": product.is_active,
        "created_at": product.created_at.isoformat() if product.created_at else None,
        "updated_at": product.updated_at.isoformat() if product.updated_at else None,
    }


def parse_price(value, field):
    if isinstance(value, bool) or value is None:
        raise ValueError(f"{field} must be a non-negative decimal.")

    try:
        price = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{field} must be a valid decimal.") from None

    if not price.is_finite() or price < 0:
        raise ValueError(f"{field} must be a non-negative decimal.")

    if price.as_tuple().exponent < -2 or price > Decimal("9999999999.99"):
        raise ValueError(f"{field} must have at most 2 decimal places and fit NUMERIC(12,2).")

    return price


def parse_nonnegative_integer(value, field):
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer.")
    return value


def validate_category(category_id):
    if category_id is None:
        return None

    if isinstance(category_id, bool) or not isinstance(category_id, int):
        raise ValueError("category_id must be an integer or null.")

    category = db.session.get(Category, category_id)
    if category is None:
        raise ValueError("The selected category does not exist.")

    return category_id


@products_bp.get("/api/products")
def list_products():
    try:
        page = int(request.args.get("page", "1"))
        per_page = int(request.args.get("per_page", "20"))

        if page < 1 or not 1 <= per_page <= 100:
            raise ValueError("page must be positive and per_page must be between 1 and 100.")

        sort_fields = {
            "id": Product.id,
            "sku": Product.sku,
            "name": Product.name,
            "cost_price": Product.cost_price,
            "selling_price": Product.selling_price,
            "quantity": Product.quantity,
            "created_at": Product.created_at,
        }
        sort = request.args.get("sort", "name")
        direction = request.args.get("direction", "asc").lower()

        if sort not in sort_fields or direction not in {"asc", "desc"}:
            raise ValueError("Invalid sort field or direction.")

        allowed = {
            "page", "per_page", "sort", "direction", "search",
            "category_id", "is_active", "stock_status",
        }
        unknown = set(request.args.keys()) - allowed
        if unknown:
            raise ValueError(f"Unsupported query parameter: {sorted(unknown)[0]}")

        query = Product.query

        search = request.args.get("search", "").strip()
        if search:
            pattern = f"%{search}%"
            query = query.filter(
                or_(Product.name.ilike(pattern), Product.sku.ilike(pattern))
            )

        if "category_id" in request.args:
            category_id = int(request.args["category_id"])
            query = query.filter(Product.category_id == category_id)

        if "is_active" in request.args:
            active = request.args["is_active"].lower()
            if active not in {"true", "false"}:
                raise ValueError("is_active must be true or false.")
            query = query.filter(Product.is_active == (active == "true"))

        stock_status = request.args.get("stock_status")
        if stock_status == "low":
            query = query.filter(
                Product.quantity > 0,
                Product.quantity <= Product.reorder_level,
            )
        elif stock_status == "out":
            query = query.filter(Product.quantity == 0)
        elif stock_status == "in_stock":
            query = query.filter(Product.quantity > 0)
        elif stock_status is not None:
            raise ValueError("stock_status must be low, out, or in_stock.")

        column = sort_fields[sort]
        query = query.order_by(
            column.asc() if direction == "asc" else column.desc(),
            Product.id.asc(),
        )

        total = query.count()
        products = query.offset((page - 1) * per_page).limit(per_page).all()

        return jsonify({
            "items": [product_json(p) for p in products],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page,
            },
        }), 200

    except (ValueError, TypeError):
        return jsonify({"error": "Invalid pagination, filter, or sorting parameters."}), 400


@products_bp.post("/api/products")
def create_product():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required."}), 400

    allowed = {
        "sku", "name", "description", "category_id",
        "cost_price", "selling_price", "quantity", "reorder_level",
    }
    if set(data) - allowed:
        return jsonify({"error": "Request contains unsupported fields."}), 400

    try:
        sku = data.get("sku")
        name = data.get("name")

        if not isinstance(sku, str) or not sku.strip() or len(sku.strip()) > 64:
            raise ValueError("SKU is required and must not exceed 64 characters.")
        if not isinstance(name, str) or not name.strip() or len(name.strip()) > 160:
            raise ValueError("Name is required and must not exceed 160 characters.")

        sku = sku.strip()
        name = name.strip()

        if db.session.scalar(
            select(Product.id).where(func.lower(Product.sku) == sku.lower())
        ):
            return jsonify({"error": "SKU already exists."}), 409

        description = data.get("description")
        if description is not None and not isinstance(description, str):
            raise ValueError("description must be a string or null.")

        product = Product(
            sku=sku,
            name=name,
            description=description,
            category_id=validate_category(data.get("category_id")),
            cost_price=parse_price(data.get("cost_price"), "cost_price"),
            selling_price=parse_price(data.get("selling_price"), "selling_price"),
            quantity=parse_nonnegative_integer(data.get("quantity", 0), "quantity"),
            reorder_level=parse_nonnegative_integer(
                data.get("reorder_level", 0), "reorder_level"
            ),
        )

        # Creating a product must not be used to bypass stock-movement auditing.
        if product.quantity != 0:
            raise ValueError(
                "Create products with quantity 0; use a stock receipt to add stock."
            )

        db.session.add(product)
        db.session.commit()
        return jsonify(product_json(product)), 201

    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "SKU or another unique field already exists."}), 409
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Unable to create product."}), 500


@products_bp.get("/api/products/<int:product_id>")
def get_product(product_id):
    product = db.session.get(Product, product_id)
    if product is None:
        return jsonify({"error": "Product not found."}), 404
    return jsonify(product_json(product)), 200


@products_bp.route("/api/products/<int:product_id>", methods=["PUT", "PATCH"])
def update_product(product_id):
    product = db.session.get(Product, product_id)
    if product is None:
        return jsonify({"error": "Product not found."}), 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data:
        return jsonify({"error": "A non-empty JSON object is required."}), 400

    editable = {
        "sku", "name", "description", "category_id",
        "cost_price", "selling_price", "reorder_level",
    }
    if set(data) - editable:
        return jsonify({
            "error": "Unsupported field. Change stock only through stock movements."
        }), 400

    try:
        if "sku" in data:
            sku = data["sku"]
            if not isinstance(sku, str) or not sku.strip() or len(sku.strip()) > 64:
                raise ValueError("SKU is required and must not exceed 64 characters.")

            sku = sku.strip()
            duplicate = db.session.scalar(
                select(Product.id).where(
                    func.lower(Product.sku) == sku.lower(),
                    Product.id != product_id,
                )
            )
            if duplicate:
                return jsonify({"error": "SKU already exists."}), 409
            product.sku = sku

        if "name" in data:
            name = data["name"]
            if not isinstance(name, str) or not name.strip() or len(name.strip()) > 160:
                raise ValueError("Name is required and must not exceed 160 characters.")
            product.name = name.strip()

        if "description" in data:
            if data["description"] is not None and not isinstance(data["description"], str):
                raise ValueError("description must be a string or null.")
            product.description = data["description"]

        if "category_id" in data:
            product.category_id = validate_category(data["category_id"])
        if "cost_price" in data:
            product.cost_price = parse_price(data["cost_price"], "cost_price")
        if "selling_price" in data:
            product.selling_price = parse_price(data["selling_price"], "selling_price")
        if "reorder_level" in data:
            product.reorder_level = parse_nonnegative_integer(
                data["reorder_level"], "reorder_level"
            )

        db.session.commit()
        return jsonify(product_json(product)), 200

    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "SKU or another unique field already exists."}), 409
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Unable to update product."}), 500


@products_bp.post("/api/products/<int:product_id>/archive")
def archive_product(product_id):
    product = db.session.get(Product, product_id)
    if product is None:
        return jsonify({"error": "Product not found."}), 404

    product.is_active = False
    try:
        db.session.commit()
        return jsonify(product_json(product)), 200
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Unable to archive product."}), 500