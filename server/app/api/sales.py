from flask import Blueprint, jsonify, request
from app.models import db, Sale, SaleItem, Product, StockMovement
from decimal import Decimal
import uuid

sales_bp = Blueprint('sales', __name__, url_prefix='/sales')

@sales_bp.route('', methods=['GET'])
def list_sales():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status_filter = request.args.get('status')

    query = Sale.query
    if status_filter:
        query = query.filter_by(status=status_filter)

    pagination = query.order_by(Sale.sold_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        "sales": [
            {
                "id": s.id,
                "sale_number": s.sale_number,
                "total_amount": float(s.total_amount),
                "status": s.status,
                "sold_at": s.sold_at.isoformat() if s.sold_at else None,
                "items": [{
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": float(item.unit_price)
                } for item in s.items]
            } for s in pagination.items
        ],
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": pagination.page
    }), 200

@sales_bp.route('/<int:sale_id>', methods=['GET'])
def get_sale_details(sale_id):
    sale = Sale.query.get(sale_id)
    if not sale:
        return jsonify({"error": "Sale not found"}), 404

    return jsonify({
        "id": sale.id,
        "sale_number": sale.sale_number,
        "total_amount": float(sale.total_amount),
        "status": sale.status,
        "sold_at": sale.sold_at.isoformat() if sale.sold_at else None,
        "items": [{
            "product_id": item.product_id,
            "quantity": item.quantity,
            "unit_price": float(item.unit_price),
            "unit_cost": float(item.unit_cost)
        } for item in sale.items]
    }), 200

@sales_bp.route('', methods=['POST'])
def create_sale():
    data = request.get_json() or {}
    items_data = data.get('items', [])
    idempotency_key = request.headers.get('X-Idempotency-Key')

    if not items_data:
        return jsonify({"error": "Sale must contain at least one item"}), 400

    if idempotency_key:
        try:
            uuid_key = uuid.UUID(idempotency_key)
            existing_sale = Sale.query.filter_by(idempotency_key=uuid_key).first()
            if existing_sale:
                return jsonify({
                    "message": "Duplicate request caught via idempotency key.",
                    "sale_id": existing_sale.id
                }), 200
        except ValueError:
            pass # Invalid UUID format, proceed normally or handle as needed

    try:
        calculated_total = Decimal('0.00')
        sale_items_to_create = []

        for item_data in items_data:
            product_id = item_data.get('product_id')
            qty = item_data.get('quantity')

            if not product_id or not qty or qty <= 0:
                return jsonify({"error": "Invalid product ID or quantity"}), 400

            # Row locking for concurrent safety using Product.quantity
            product = Product.query.with_for_update().get(product_id)
            if not product:
                db.session.rollback()
                return jsonify({"error": f"Product {product_id} not found"}), 404

            if product.quantity < qty:
                db.session.rollback()
                return jsonify({"error": f"Insufficient stock for product ID {product_id}. Available: {product.quantity}"}), 400

            # Mapped to selling_price and cost_price from models.py
            unit_price = Decimal(str(product.selling_price))
            unit_cost = Decimal(str(product.cost_price))
            calculated_total += (unit_price * qty)

            product.quantity -= qty

            sale_items_to_create.append({
                "product": product,
                "quantity": qty,
                "unit_price": unit_price,
                "unit_cost": unit_cost
            })

        # Generate unique sale number and assign a default user_id (e.g., 1 or from request context)
        sale_number = f"SALE-{uuid.uuid4().hex[:8].upper()}"
        
        new_sale = Sale(
            sale_number=sale_number,
            user_id=1, # Replace with current authenticated user ID if available
            subtotal=calculated_total,
            total_amount=calculated_total,
            status='completed',
            idempotency_key=uuid.UUID(idempotency_key) if idempotency_key else None
        )
        db.session.add(new_sale)
        db.session.flush()

        for item in sale_items_to_create:
            line_total = item["unit_price"] * item["quantity"]
            sale_item = SaleItem(
                sale_id=new_sale.id,
                product_id=item["product"].id,
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                unit_cost=item["unit_cost"],
                line_total=line_total
            )
            db.session.add(sale_item)

            # Fixed StockMovement column (quantity_change) and allowed movement_type ('sale')
            movement = StockMovement(
                product_id=item["product"].id,
                quantity_change=-item["quantity"],
                movement_type='sale',
                reference_type='sale',
                reference_id=new_sale.id,
                reason=f"Sale order {sale_number}"
            )
            db.session.add(movement)

        db.session.commit()
        return jsonify({"message": "Sale created successfully", "sale_id": new_sale.id, "total": float(calculated_total)}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@sales_bp.route('/<int:sale_id>/refund', methods=['POST'])
def refund_sale(sale_id):
    sale = Sale.query.get(sale_id)
    if not sale:
        return jsonify({"error": "Sale not found"}), 404

    if sale.status == 'refunded':
        return jsonify({"error": "Sale has already been refunded"}), 400

    try:
        sale.status = 'refunded'

        for item in sale.items:
            product = Product.query.with_for_update().get(item.product_id)
            if product:
                product.quantity += item.quantity

                # Fixed StockMovement column (quantity_change) and allowed movement_type ('return')
                movement = StockMovement(
                    product_id=product.id,
                    quantity_change=item.quantity,
                    movement_type='return',
                    reference_type='sale',
                    reference_id=sale.id,
                    reason=f"Refund for sale {sale.sale_number}"
                )
                db.session.add(movement)

        db.session.commit()
        return jsonify({"message": f"Sale {sale_id} successfully refunded and stock restored."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500