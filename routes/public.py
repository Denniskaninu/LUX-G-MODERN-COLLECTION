from flask import Blueprint, render_template, request, jsonify
from models import Product
from sqlalchemy import func
from app import db
from flask import Blueprint, render_template, request, jsonify, send_file, current_app
import os
public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    """Public gallery with search and filtering"""
    search_query = request.args.get('q', '').strip()
    category_filter = request.args.get('category', '').strip()
    
    # Base query for deduplication - get one representative per canonical key
    subquery = db.session.query(
        func.min(Product.id).label('min_id')
    ).filter(
        Product.quantity > 0
    ).group_by(
        Product.category,
        Product.name,
        Product.brand,
        Product.color,
        Product.size
    ).subquery()
    
    query = db.session.query(Product).filter(
        Product.id.in_(db.session.query(subquery.c.min_id))
    )
    
    # Apply search filter
    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            db.or_(
                Product.name.ilike(search_pattern),
                Product.category.ilike(search_pattern),
                Product.brand.ilike(search_pattern),
                Product.color.ilike(search_pattern)
            )
        )
    
    # Apply category filter
    if category_filter:
        query = query.filter(Product.category == category_filter)
    
    products = query.order_by(Product.created_at.desc()).all()
    
    # Get categories for filter chips
    categories = db.session.query(Product.category).filter(
        Product.quantity > 0
    ).distinct().all()
    categories = [cat[0] for cat in categories]
    
    return render_template('public/index.html', 
                         products=products, 
                         categories=categories,
                         search_query=search_query,
                         current_category=category_filter)

@public_bp.route('/about')
def about():
    """About page with store info"""
    return render_template('public/about.html')


@public_bp.route('/uploads/<path:filename>')
def serve_uploaded_file(filename):
    """Serve uploaded images"""
    try:
        # Handle case where filename might already include 'uploads/' prefix
        if filename.startswith('uploads/'):
            file_path = os.path.join(current_app.root_path, filename)
        else:
            file_path = os.path.join(current_app.root_path, 'uploads', filename)
            
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            return "Image not found", 404
    except Exception as e:
        return f"Error serving image: {str(e)}", 500