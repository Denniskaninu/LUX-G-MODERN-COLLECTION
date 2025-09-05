from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from models import Product, Sale, AdminUser
from forms import ProductForm, SellForm, RestockForm
from routes.auth import login_required
from utils import process_image
from app import db
from sqlalchemy import func
from decimal import Decimal
import os

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
@login_required
def dashboard():
    """Admin dashboard with key metrics"""
    # Calculate metrics
    total_stock = db.session.query(func.sum(Product.quantity)).scalar() or 0
    
    net_worth_bp = db.session.query(
        func.sum(Product.bp * Product.quantity)
    ).scalar() or Decimal('0')
    
    net_worth_sp = db.session.query(
        func.sum(Product.sp * Product.quantity)
    ).scalar() or Decimal('0')
    
    # Weekly profit (last 7 days)
    from datetime import datetime, timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    weekly_profit = db.session.query(
        func.sum(Sale.profit)
    ).filter(Sale.sold_at >= week_ago).scalar() or Decimal('0')
    
    # Monthly profit
    month_ago = datetime.utcnow() - timedelta(days=30)
    monthly_profit = db.session.query(
        func.sum(Sale.profit)
    ).filter(Sale.sold_at >= month_ago).scalar() or Decimal('0')
    
    # Recent sales
    recent_sales = Sale.query.order_by(Sale.sold_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_stock=total_stock,
                         net_worth_bp=net_worth_bp,
                         net_worth_sp=net_worth_sp,
                         weekly_profit=weekly_profit,
                         monthly_profit=monthly_profit,
                         recent_sales=recent_sales)

@admin_bp.route('/products')
@login_required
def products():
    """List all products with management options"""
    search_query = request.args.get('q', '').strip()
    category_filter = request.args.get('category', '').strip()
    
    query = Product.query
    
    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            db.or_(
                Product.name.ilike(search_pattern),
                Product.brand.ilike(search_pattern),
                Product.sku.ilike(search_pattern)
            )
        )
    
    if category_filter:
        query = query.filter(Product.category == category_filter)
    
    products = query.order_by(Product.updated_at.desc()).all()
    
    # Get categories for filter
    categories = db.session.query(Product.category).distinct().all()
    categories = [cat[0] for cat in categories]
    
    return render_template('admin/products.html', 
                         products=products, 
                         categories=categories,
                         search_query=search_query,
                         current_category=category_filter)

@admin_bp.route('/products/new', methods=['GET', 'POST'])
@login_required
def upload_product():
    """Upload new product"""
    form = ProductForm()
    
    if form.validate_on_submit():
        try:
            # Process image
            original_path, web_path = process_image(form.image.data)
            
            # Create product
            product = Product(
                name=form.name.data,
                category=form.category.data,
                brand=form.brand.data,
                color=form.color.data,
                size=form.size.data,
                sku=form.sku.data if form.sku.data else None,
                bp=form.bp.data,
                sp=form.sp.data,
                quantity=form.quantity.data,
                image_path_original=original_path,
                image_path_web=web_path
            )
            
            db.session.add(product)
            db.session.commit()
            
            flash(f'Product "{product.name}" uploaded successfully!', 'success')
            return redirect(url_for('admin.products'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error uploading product: {e}")
            flash('Error uploading product. Please try again.', 'error')
    
    return render_template('admin/upload.html', form=form)

@admin_bp.route('/products/<int:product_id>/sell', methods=['POST'])
@login_required
def sell_product(product_id):
    """Sell product"""
    product = Product.query.get_or_404(product_id)
    
    selling_price = Decimal(request.form.get('selling_price', '0'))
    quantity_to_sell = int(request.form.get('quantity', '0'))
    
    # Validation
    if quantity_to_sell <= 0:
        flash('Quantity must be greater than 0.', 'error')
        return redirect(url_for('admin.products'))
    
    if quantity_to_sell > product.quantity:
        flash(f'Cannot sell {quantity_to_sell} items. Only {product.quantity} available.', 'error')
        return redirect(url_for('admin.products'))
    
    if selling_price <= 0:
        flash('Selling price must be greater than 0.', 'error')
        return redirect(url_for('admin.products'))
    
    try:
        # Create sale record
        profit = (selling_price - product.bp) * quantity_to_sell
        
        sale = Sale(
            product_id=product.id,
            quantity=quantity_to_sell,
            sp_at_sale=selling_price,
            bp_at_sale=product.bp,
            profit=profit
        )
        
        # Update product quantity
        product.quantity -= quantity_to_sell
        
        db.session.add(sale)
        db.session.commit()
        
        flash(f'Umeuza {quantity_to_sell} × {product.name}. Profit: KSh {profit:,.2f}', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error recording sale: {e}")
        flash('Error recording sale. Please try again.', 'error')
    
    return redirect(url_for('admin.products'))

@admin_bp.route('/products/<int:product_id>/restock', methods=['POST'])
@login_required
def restock_product(product_id):
    """Restock product"""
    product = Product.query.get_or_404(product_id)
    
    quantity_to_add = int(request.form.get('quantity', '0'))
    
    if quantity_to_add <= 0:
        flash('Quantity must be greater than 0.', 'error')
        return redirect(url_for('admin.products'))
    
    try:
        product.quantity += quantity_to_add
        db.session.commit()
        
        flash(f'Added {quantity_to_add} units to {product.name}. New stock: {product.quantity}', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error restocking: {e}")
        flash('Error restocking product. Please try again.', 'error')
    
    return redirect(url_for('admin.products'))

@admin_bp.route('/products/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    """Delete product (only if no sales)"""
    product = Product.query.get_or_404(product_id)
    
    # Check if product has sales
    if Sale.query.filter_by(product_id=product.id).first():
        flash('Cannot delete product with sales history.', 'error')
        return redirect(url_for('admin.products'))
    
    try:
        # Delete image files
        if product.image_path_original:
            original_path = os.path.join(current_app.root_path, product.image_path_original)
            if os.path.exists(original_path):
                os.remove(original_path)
        
        if product.image_path_web:
            web_path = os.path.join(current_app.root_path, product.image_path_web)
            if os.path.exists(web_path):
                os.remove(web_path)
        
        db.session.delete(product)
        db.session.commit()
        
        flash(f'Product "{product.name}" deleted successfully.', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting product: {e}")
        flash('Error deleting product. Please try again.', 'error')
    
    return redirect(url_for('admin.products'))
