from flask import Blueprint, render_template, request, make_response, current_app
from models import Sale, Product
from routes.auth import login_required
from app import db
from sqlalchemy import func
from datetime import datetime, timedelta
import csv
import io

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/')
@login_required
def reports():
    """Sales reports with period filtering"""
    period = request.args.get('period', 'week')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    
    # Calculate date range
    now = datetime.utcnow()
    
    if period == 'week':
        start_date = now - timedelta(days=6)
        end_date = now
        title = "This Week"
    elif period == 'month':
        start_date = now.replace(day=1)
        end_date = now
        title = "This Month"
    elif period == 'year':
        start_date = now.replace(month=1, day=1)
        end_date = now
        title = "This Year"
    elif period == 'custom' and from_date and to_date:
        try:
            start_date = datetime.strptime(from_date, '%Y-%m-%d')
            end_date = datetime.strptime(to_date, '%Y-%m-%d')
            title = f"{from_date} to {to_date}"
        except ValueError:
            start_date = now - timedelta(days=6)
            end_date = now
            title = "This Week"
            period = 'week'
    else:
        start_date = now - timedelta(days=6)
        end_date = now
        title = "This Week"
        period = 'week'
    
    # Query sales in the period
    sales_query = Sale.query.filter(
        Sale.sold_at >= start_date,
        Sale.sold_at <= end_date
    )
    
    sales = sales_query.order_by(Sale.sold_at.desc()).all()
    
    # Calculate metrics
    total_revenue = sum(sale.sp_at_sale * sale.quantity for sale in sales)
    total_cogs = sum(sale.bp_at_sale * sale.quantity for sale in sales)
    total_profit = total_revenue - total_cogs
    total_units = sum(sale.quantity for sale in sales)
    
    # Group sales by date for chart data
    daily_sales = {}
    for sale in sales:
        date_key = sale.sold_at.strftime('%Y-%m-%d')
        if date_key not in daily_sales:
            daily_sales[date_key] = {'revenue': 0, 'profit': 0}
        daily_sales[date_key]['revenue'] += float(sale.sp_at_sale * sale.quantity)
        daily_sales[date_key]['profit'] += float(sale.profit)
    
    return render_template('admin/reports.html',
                         sales=sales,
                         total_revenue=total_revenue,
                         total_cogs=total_cogs,
                         total_profit=total_profit,
                         total_units=total_units,
                         period=period,
                         title=title,
                         from_date=from_date,
                         to_date=to_date,
                         daily_sales=daily_sales)

@reports_bp.route('/export.csv')
@login_required
def export_csv():
    """Export sales data as CSV"""
    period = request.args.get('period', 'week')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    
    # Calculate date range (same logic as reports)
    now = datetime.utcnow()
    
    if period == 'week':
        start_date = now - timedelta(days=6)
        end_date = now
    elif period == 'month':
        start_date = now.replace(day=1)
        end_date = now
    elif period == 'year':
        start_date = now.replace(month=1, day=1)
        end_date = now
    elif period == 'custom' and from_date and to_date:
        try:
            start_date = datetime.strptime(from_date, '%Y-%m-%d')
            end_date = datetime.strptime(to_date, '%Y-%m-%d')
        except ValueError:
            start_date = now - timedelta(days=6)
            end_date = now
    else:
        start_date = now - timedelta(days=6)
        end_date = now
    
    # Query sales
    sales = Sale.query.filter(
        Sale.sold_at >= start_date,
        Sale.sold_at <= end_date
    ).order_by(Sale.sold_at.desc()).all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Date', 'Product Name', 'Category', 'Quantity', 
        'Buying Price', 'Selling Price', 'Profit'
    ])
    
    # Write data
    for sale in sales:
        writer.writerow([
            sale.sold_at.strftime('%Y-%m-%d %H:%M'),
            sale.product.name,
            sale.product.category,
            sale.quantity,
            f'{sale.bp_at_sale:.2f}',
            f'{sale.sp_at_sale:.2f}',
            f'{sale.profit:.2f}'
        ])
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=sales_report_{period}.csv'
    
    return response
