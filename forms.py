from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, DecimalField, IntegerField, SelectField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, NumberRange, Optional, Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(max=200)])
    category = SelectField('Category', choices=[
        ('Shoes', 'Shoes'),
        ('Clothes', 'Clothes'),
        ('Bags', 'Bags'),
        ('Accessories', 'Accessories')
    ], validators=[DataRequired()])
    brand = StringField('Brand', validators=[Optional(), Length(max=100)])
    color = StringField('Color', validators=[Optional(), Length(max=50)])
    size = StringField('Size', validators=[Optional(), Length(max=50)])
    sku = StringField('SKU (Optional)', validators=[Optional(), Length(max=100)])
    bp = DecimalField('Buying Price (KSh)', validators=[DataRequired(), NumberRange(min=0)], places=2)
    sp = DecimalField('Selling Price (KSh)', validators=[DataRequired(), NumberRange(min=0)], places=2)
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    image = FileField('Product Image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Images only!')
    ])

class SellForm(FlaskForm):
    selling_price = DecimalField('Selling Price (KSh)', validators=[DataRequired(), NumberRange(min=0)], places=2)
    quantity = IntegerField('Quantity to Sell', validators=[DataRequired(), NumberRange(min=1)])

class RestockForm(FlaskForm):
    quantity = IntegerField('Quantity to Add', validators=[DataRequired(), NumberRange(min=1)])
