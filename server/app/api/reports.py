from flask import Blueprint, jsonify, request, Response
from app.models import db, Sale, SaleItem, Product, StockMovement
from sqlalchemy import func
from datetime import datetime
import csv
import io

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/dashboard', methods=['GET'])
def get_dashboard():

    total_products = db.session.query(func.count(Product.id)).scalar() or 0
    total_stock_value = db.session.query(func.sum(Product.stock_level * Product.cost)).scalar() or 0
    low_stock_count = db.session.query(func.count(Product.id)).filter(Product.stock_level <= Product.reorder_level).scalar() or 0
    total_sales_revenue = db.session.query(func.sum(Sale.total_amount)).filter(Sale.status == 'completed').scalar() or 0

    return jsonify({
        "metrics": {
            "total_products": total_products,
            "total_stock_valuation": float(total_stock_value),
            "low_stock_items_count": low_stock_count,
            "total_sales_revenue": float(total_sales_revenue)
        },
        "definitions": {
            "revenue": "Total money earned from completed (non-refunded) sales.",
            "gross_profit": "Revenue minus the original cost of the items sold (COGS).",
            "refunds": "Total value of returned or canceled sales.",
            "stock_valuation": "Total financial asset value of current stock on hand (Quantity * Cost)."
        }
    }), 200

@reports_bp.route('/reports/sales', methods=['sales-report']) # accessible via /api/reports/sales due to prefix structure
@reports_bp.route('/sales', methods=['GET'])
def sales_report():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    export_format = request.args.get('format') # Pass ?format=csv to download

    query = Sale.query
    if start_date:
        query = query.filter(Sale.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Sale.created_at <= datetime.fromisoformat(end_date))

    sales = query.all()

    completed_sales = [s for s in sales if s.status == 'completed']
    refunded_sales = [s for s in sales if s.status == 'refunded']

    total_revenue = sum(s.total_amount for s in completed_sales)
    total_refunds = sum(s.total_amount for s in refunded_sales)
    total_cost = sum(item.unit_cost * item.quantity for s in completed_sales for item in s.items)
    gross_profit = total_revenue - total_cost

    data = {
        "completed_sales_count": len(completed_sales),
        "total_revenue": float(total_revenue),
        "total_refunds": float(total_refunds),
        "cost_of_goods_sold": float(total_cost),
        "gross_profit": float(gross_profit)
    }

    # Safe CSV Export handling
    if export_format == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Metric", "Value"])
        for key, val in data.items():
            writer.writerow([key, val])
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=sales_report.csv"}
        )

    return jsonify(data), 200

@reports_bp.route('/inventory', methods=['GET'])
def inventory_report():
    export_format = request.args.get('format')
    products = Product.query.all()

    report_data = []
    for p in products:
        valuation = float(p.stock_level * p.cost)
        report_data.append({
            "product_id": p.id,
            "name": p.name,
            "stock_level": p.stock_level,
            "unit_cost": float(p.cost),
            "stock_valuation": valuation
        })

    if export_format == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Product ID", "Name", "Stock Level", "Unit Cost", "Stock Valuation"])
        for row in report_data:
            writer.writerow([row["product_id"], row["name"], row["stock_level"], row["unit_cost"], row["stock_valuation"]])
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=inventory_valuation.csv"}
        )

    return jsonify({"inventory_report": report_data}), 200

@reports_bp.route('/low-stock', methods=['GET'])
def low_stock_report():
    products = Product.query.filter(Product.stock_level <= Product.reorder_level).all()
    return jsonify({
        "low_stock_products": [{
            "id": p.id,
            "name": p.name,
            "stock_level": p.stock_level,
            "reorder_level": p.reorder_level
        } for p in products]
    }), 200

@reports_bp.route('/stock-movements', methods=['GET'])
def stock_movements_report():
    movements = StockMovement.query.order_by(StockMovement.created_at.desc()).limit(100).all()
    return jsonify({
        "movements": [{
            "id": m.id,
            "product_id": m.product_id,
            "quantity": m.quantity,
            "movement_type": m.movement_type,
            "reference_id": m.reference_id,
            "created_at": m.created_at.isoformat() if m.created_at else None
        } for m in movements]
    }), 200