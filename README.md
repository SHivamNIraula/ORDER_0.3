# Restaurant Order Management System

A Django-based restaurant order management system with real-time functionality and PostgreSQL database.

## Features

- **User Authentication** - Registration, login, logout
- **Table Management** - Table selection and reservation
- **Food Ordering** - Menu browsing and cart management
- **Order Processing** - Order creation and tracking
- **Payment System** - Payment processing and confirmation
- **Real-time Updates** - Django Channels integration
- **PostgreSQL Database** - Robust data storage

## Project Structure

```
restaurant_system/
├── authentication/     # User authentication app
├── tables/            # Table management app
├── food/              # Food menu and ordering app
├── orders/            # Order processing app
├── payment/           # Payment handling app
├── restaurant_system/ # Main project settings
├── restaurant_env/    # Virtual environment
├── requirements.txt   # Dependencies
└── manage.py         # Django management script
```

## Setup Instructions

### 1. Database Setup
Create PostgreSQL database:
```sql
CREATE DATABASE restaurant_system_db;
GRANT ALL PRIVILEGES ON DATABASE restaurant_system_db TO restaurant_user;
ALTER USER restaurant_user WITH SUPERUSER;
```

### 2. Run Migrations
```bash
cd RESTAURANT_ORDER_SYSTEM
restaurant_env/Scripts/python.exe manage.py migrate
```

### 3. Create Superuser
```bash
restaurant_env/Scripts/python.exe manage.py createsuperuser
```

### 4. Run Development Server
```bash
restaurant_env/Scripts/python.exe manage.py runserver
```

## Access Points

- **Main Application**: http://127.0.0.1:8000/
- **Admin Interface**: http://127.0.0.1:8000/admin/
- **User Authentication**: http://127.0.0.1:8000/auth/login/

## Technology Stack

- **Backend**: Django 4.2.7
- **Database**: PostgreSQL
- **Real-time**: Django Channels
- **Frontend**: Bootstrap 5
- **Forms**: Django Crispy Forms
- **Static Files**: WhiteNoise

## Next Development Steps

1. Implement table models and views
2. Create food menu system
3. Build shopping cart functionality
4. Add order processing logic
5. Integrate payment system
6. Add real-time notifications
7. Enhance UI/UX design

## Apps Overview

- **authentication**: Handles user registration, login, and session management
- **tables**: Manages restaurant table selection and reservations
- **food**: Contains food menu, categories, and item management
- **orders**: Processes customer orders and cart functionality
- **payment**: Handles payment processing and transaction management