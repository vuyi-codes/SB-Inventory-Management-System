from flask import Blueprint, jsonify, request
from app.models import db, Supplier

suppliers_bp = Blueprint('suppliers', __name__, url_prefix='/api/suppliers')

def serialize_supplier(s):
    return {
        "id": s.id,
        "name": s.name,
        "contact_person": s.contact_person,
        "email": s.email,
        "phone": s.phone,
        "address": s.address
    }

@suppliers_bp.route('', methods=['GET'])
def get_suppliers():
    suppliers = Supplier.query.all()
    return jsonify([serialize_supplier(s) for s in suppliers]), 200

@suppliers_bp.route('/<int:supplier_id>', methods=['GET'])
def get_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    return jsonify(serialize_supplier(supplier)), 200

@suppliers_bp.route('', methods=['POST'])
def create_supplier():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({"error": "Supplier name is required"}), 400
        
    supplier = Supplier(
        name=data['name'],
        contact_person=data.get('contact_person'),
        email=data.get('email'),
        phone=data.get('phone'),
        address=data.get('address')
    )
    db.session.add(supplier)
    db.session.commit()
    return jsonify(serialize_supplier(supplier)), 201

@suppliers_bp.route('/<int:supplier_id>', methods=['PUT'])
def update_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    supplier.name = data.get('name', supplier.name)
    supplier.contact_person = data.get('contact_person', supplier.contact_person)
    supplier.email = data.get('email', supplier.email)
    supplier.phone = data.get('phone', supplier.phone)
    supplier.address = data.get('address', supplier.address)

    db.session.commit()
    return jsonify(serialize_supplier(supplier)), 200

@suppliers_bp.route('/<int:supplier_id>', methods=['DELETE'])
def delete_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    db.session.delete(supplier)
    db.session.commit()
    return jsonify({"message": "Supplier deleted successfully"}), 200