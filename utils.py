import os
import uuid
from PIL import Image
from werkzeug.utils import secure_filename
from flask import current_app

def process_image(image_file):
    """
    Process uploaded image: save original and create web-optimized version
    Returns tuple of (original_path, web_path)
    """
    # Generate unique filename
    file_ext = os.path.splitext(secure_filename(image_file.filename))[1].lower()
    if not file_ext:
        file_ext = '.jpg'
    
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    
    # Paths
    original_path = os.path.join('uploads', 'original', unique_filename)
    web_path = os.path.join('uploads', 'web', unique_filename)
    
    # Save original
    original_full_path = os.path.join(current_app.root_path, original_path)
    image_file.save(original_full_path)
    
    # Create web-optimized version
    web_full_path = os.path.join(current_app.root_path, web_path)
    
    try:
        with Image.open(original_full_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Calculate optimal size maintaining aspect ratio
            max_width = 800
            max_height = 600
            
            # Calculate scaling factor
            width_ratio = max_width / img.width
            height_ratio = max_height / img.height
            scale_factor = min(width_ratio, height_ratio, 1.0)  # Don't upscale
            
            if scale_factor < 1.0:
                new_width = int(img.width * scale_factor)
                new_height = int(img.height * scale_factor)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save with optimization
            img.save(web_full_path, 'JPEG', quality=85, optimize=True)
            
    except Exception as e:
        current_app.logger.error(f"Error processing image: {e}")
        # If processing fails, copy original to web
        import shutil
        shutil.copy2(original_full_path, web_full_path)
    
    return original_path, web_path

def slugify(text):
    """Convert text to slug"""
    import re
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s\-]', '', text)
    text = re.sub(r'[\s\-]+', '-', text)
    return text.strip('-')
