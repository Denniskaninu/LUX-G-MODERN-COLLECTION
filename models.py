from app import db
from datetime import datetime
from decimal import Decimal
import re

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100))
    color = db.Column(db.String(50))
    size = db.Column(db.String(50))
    sku = db.Column(db.String(100), unique=True)
    bp = db.Column(db.Numeric(10, 2), nullable=False)  # buying price
    sp = db.Column(db.Numeric(10, 2), nullable=False)  # selling price
    quantity = db.Column(db.Integer, nullable=False, default=0)
    image_path_original = db.Column(db.String(255))
    image_path_web = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    sales = db.relationship('Sale', backref='product', lazy=True)
    
    # Add constraint for quantity >= 0
    __table_args__ = (
        db.CheckConstraint('quantity >= 0', name='check_quantity_positive'),
    )
    
    @property
    def canonical_key(self):
        """Generate canonical key for deduplication"""
        if self.sku:
            return self.sku.lower()
        
        # Create key from category|name|brand|color|size
        parts = [
            self.category or '',
            self.name or '',
            self.brand or '',
            self.color or '',
            self.size or ''
        ]
        key = '|'.join(parts).lower()
        # Remove special characters and normalize
        return re.sub(r'[^a-z0-9|]', '', key)
    
    def __repr__(self):
        return f'<Product {self.name}>'

class Sale(db.Model):
    __tablename__ = 'sales'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='RESTRICT'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    sp_at_sale = db.Column(db.Numeric(10, 2), nullable=False)  # selling price at time of sale
    bp_at_sale = db.Column(db.Numeric(10, 2), nullable=False)  # buying price at time of sale
    profit = db.Column(db.Numeric(10, 2), nullable=False)  # computed profit
    sold_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Add constraint for quantity > 0
    __table_args__ = (
        db.CheckConstraint('quantity > 0', name='check_sale_quantity_positive'),
    )
    
    def __repr__(self):
        return f'<Sale {self.product.name} x{self.quantity}>'

class AdminUser(db.Model):
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AdminUser {self.username}>'
