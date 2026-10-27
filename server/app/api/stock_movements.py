from datetime import datetime, timezone

from flask import Blueprint, g, jsonify, request
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import Product, StockMovement, User
from app.services.inventory import (
    ALLOWED_MOVEMENT_TYPES,
    InventoryError,
    record_stock_movement,
)

stock_movements_bp = Blueprint("stock_movements", __name__)


def movement_json(movement):
    return {
        "id": movement.id,
        "product_id": movement.product_id,
        "product_name": movement.product.name if movement.product else None,
        "sku": movement.product.sku if movement.product else None,
        "user_id": movement.user_id,
        "actor_name": movement.user.name if movement.user else None,
        "movement_type": movement.movement_type,
        "quantity_change": movement.quantity_change,
        "reason": movement.reason,
        "created_at": (
            movement.created_at.isoformat() if movement.created_at else None
        ),
    }


@stock_movements_bp.get("/api/stock-movements")
def list_stock_movements():
    try:
        page = int(request.args.get("page", "1"))
        per_page = int(request.args.get("per_page", "20"))

        if page < 1 or not 1 <= per_page <= 100:
            raise ValueError

        allowed = {
            "page", "per_page", "product_id",
            "movement_type", "user_id", "start_date", "end_date",
        }

        if set(request.args.keys()) - allowed:
            return jsonify({"error": "Unsupported query parameter."}), 400

        query = StockMovement.query

        if "product_id" in request.args:
            product_id = int(request.args["product_id"])
            if product_id < 1:
                raise ValueError
            query = query.filter(StockMovement.product_id == product_id)

        if "user_id" in request.args:
            user_id = int(request.args["user_id"])
            if user_id < 1:
                raise ValueError
            query = query.filter(StockMovement.user_id == user_id)

        if "movement_type" in request.args:
            movement_type = request.args["movement_type"]
            if movement_type not in ALLOWED_MOVEMENT_TYPES:
                return jsonify({"error": "Invalid movement type."}), 400
            query = query.filter(
                StockMovement.movement_type == movement_type
            )

        if "start_date" in request.args:
            start = datetime.fromisoformat(
                request.args["start_date"].replace("Z", "+00:00")
            )
            if start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)
            query = query.filter(StockMovement.created_at >= start)

        if "end_date" in request.args:
            end = datetime.fromisoformat(
                request.args["end_date"].replace("Z", "+00:00")
            )
            if end.tzinfo is None:
                end = end.replace(tzinfo=timezone.utc)
            query = query.filter(StockMovement.created_at <= end)

        total = query.count()

        movements = (
            query.order_by(
                StockMovement.created_at.desc(),
                StockMovement.id.desc(),
            )
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        return jsonify({
            "items": [movement_json(m) for m in movements],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page,
            },
        }), 200

    except (ValueError, TypeError):
        return jsonify({"error": "Invalid filter, date, or pagination value."}), 400


@stock_movements_bp.post("/api/stock-movements")
def create_stock_movement():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required."}), 400

    allowed = {"product_id", "movement_type", "quantity_change", "reason"}
    if set(data) - allowed:
        return jsonify({"error": "Unsupported fields supplied."}), 400

    required = allowed
    if not required.issubset(data):
        return jsonify({"error": "All stock movement fields are required."}), 400

    product_id = data["product_id"]
    movement_type = data["movement_type"]
    quantity_change = data["quantity_change"]
    reason = data["reason"]

    if (
        isinstance(product_id, bool)
        or not isinstance(product_id, int)
        or product_id < 1
    ):
        return jsonify({"error": "product_id must be a positive integer."}), 400

    # IMPORTANT:
    # Your existing authentication middleware must set g.current_user
    # to the authenticated database User. Never accept user_id from JSON.
    user = getattr(g, "current_user", None)

    if not isinstance(user, User) or not user.is_active:
        return jsonify({"error": "Authentication is required."}), 401

    try:
        result = record_stock_movement(
            product_id=product_id,
            movement_type=movement_type,
            quantity_change=quantity_change,
            reason=reason,
            user_id=user.id,
        )

        return jsonify({
            "movement": movement_json(result["movement"]),
            "product": {
                "id": result["product"].id,
                "sku": result["product"].sku,
                "name": result["product"].name,
                "quantity": result["product"].quantity,
            },
        }), 201

    except InventoryError as exc:
        return jsonify({"error": str(exc)}), 400

    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Unable to record stock movement."}), 500

    except Exception:
        db.session.rollback()
        raise