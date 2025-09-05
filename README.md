# Kubwa Closet - Flask Shop Web App

A comprehensive Flask-based inventory management system for a Kenyan clothing shop featuring a public gallery and admin POS functionality.

## Features

### Public Site
- **Product Gallery**: Beautiful responsive grid displaying products without prices
- **Search & Filter**: Search by name, category, brand with category filtering
- **Mobile-First Design**: Optimized for mobile devices with Kenyan-flavoured copy
- **Product Deduplication**: Shows unique products even if multiple identical items exist

### Admin Panel
- **Secure Access**: Secret URL path with session-based authentication
- **Inventory Management**: Add, edit, restock, and sell products
- **Mobile Camera Support**: Take photos directly from mobile devices
- **Image Optimization**: Automatic resize and compression for web display
- **Sales Tracking**: Record sales with profit/loss calculations
- **Financial Reports**: Weekly, monthly, yearly reports with CSV export
- **Dashboard**: Real-time metrics including stock levels and net worth

## Tech Stack

- **Backend**: Flask, SQLAlchemy, SQLite with WAL mode
- **Frontend**: Bootstrap 5, Vanilla JavaScript, responsive design
- **Image Processing**: Pillow for automatic optimization
- **Security**: CSRF protection, secure sessions, password hashing
- **Database**: SQLite with foreign key constraints and transactions

## Local Setup on Kali Linux

### Prerequisites

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+ and pip
sudo apt install python3 python3-pip python3-venv -y

# Install additional dependencies
sudo apt install python3-dev libpq-dev build-essential -y
