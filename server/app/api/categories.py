from flask import Blueprint, jsonify, request
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.extensions import db
from app.models import Category, Product

categories_bp = Blueprint("categories", __name__)


def category_json(category):
    return {
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "created_at": (
            category.created_at.isoformat() if category.created_at else None
        ),
        "updated_at": (
            category.updated_at.isoformat() if category.updated_at else None
        ),
    }


@categories_bp.get("/api/categories")
def list_categories():
    categories = Category.query.order_by(Category.name.asc()).all()
    return jsonify({
        "items": [category_json(c) for c in categories],
        "total": len(categories),
    }), 200


@categories_bp.post("/api/categories")
def create_category():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required."}), 400

    if set(data) - {"name", "description"}:
        return jsonify({"error": "Unsupported fields supplied."}), 400

    name = data.get("name")
    description = data.get("description")

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Category name is required."}), 400

    name = name.strip()

    if len(name) > 100:
        return jsonify({"error": "Category name cannot exceed 100 characters."}), 400

    if description is not None and not isinstance(description, str):
        return jsonify({"error": "Description must be a string or null."}), 400

    duplicate = db.session.scalar(
        select(Category.id).where(func.lower(Category.name) == name.lower())
    )
    if duplicate:
        return jsonify({"error": "Category name already exists."}), 409

    category = Category(name=name, description=description)

    try:
        db.session.add(category)
        db.session.commit()
        return jsonify(category_json(category)), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Category name already exists."}), 409

    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Unable to create category."}), 500


@categories_bp.get("/api/categories/<int:category_id>")
def get_category(category_id):
    category = db.session.get(Category, category_id)

    if category is None:
        return jsonify({"error": "Category not found."}), 404

    return jsonify(category_json(category)), 200


@categories_bp.patch("/api/categories/<int:category_id>")
def update_category(category_id):
    category = db.session.get(Category, category_id)

    if category is None:
        return jsonify({"error": "Category not found."}), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({"error": "A non-empty JSON object is required."}), 400

    if set(data) - {"name", "description"}:
        return jsonify({"error": "Unsupported fields supplied."}), 400

    if "name" in data:
        name = data["name"]

        if not isinstance(name, str) or not name.strip():
            return jsonify({"error": "Category name cannot be empty."}), 400

        name = name.strip()

        if len(name) > 100:
            return jsonify({"error": "Category name cannot exceed 100 characters."}), 400

        duplicate = db.session.scalar(
            select(Category.id).where(
                func.lower(Category.name) == name.lower(),
                Category.id != category_id,
            )
        )

        if duplicate:
            return jsonify({"error": "Category name already exists."}), 409

        category.name = name

    if "description" in data:
        description = data["description"]

        if description is not None and not isinstance(description, str):
            return jsonify({"error": "Description must be a string or null."}), 400

        category.description = description

    try:
        db.session.commit()
        return jsonify(category_json(category)), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Category name already exists."}), 409

    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Unable to update category."}), 500