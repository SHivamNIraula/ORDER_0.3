# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django-based restaurant order management system with real-time functionality using Django Channels and WebSockets. The system handles user authentication, table management, food ordering, order processing, and payment handling. The project is configured for PostgreSQL database with Django Channels for real-time features.

## Architecture

The project follows Django's app-based architecture with six main applications:

- **authentication**: User registration, login, and session management
- **tables**: Table selection and reservation system
- **food**: Food menu, categories, and item management  
- **orders**: Order creation, processing, and cart functionality
- **payment**: Payment processing and transaction handling
- **admin_panel**: Staff dashboard with real-time order monitoring, income reports, and management tools

Key architectural patterns:
- Django Channels with ASGI for real-time WebSocket support
- PostgreSQL database with psycopg2-binary
- Crispy Forms with Bootstrap 5 for UI
- WhiteNoise for static file serving
- In-memory channel layers for development

## Development Commands

### Environment Setup
The project uses a virtual environment located at `restaurant_env/`. Use Windows-style paths for activation:

```bash
# Activate virtual environment
restaurant_env/Scripts/activate

# Install dependencies
pip install -r requirements.txt
```

### Django Management

**IMPORTANT**: For real-time features to work, you must start Redis server before running Daphne.

```bash
# Start Redis server (required for WebSocket functionality)
# Windows: redis-server.exe
# Linux/Mac: redis-server

# Run development server with WebSocket support (REQUIRED for real-time features)
# IMPORTANT: Make sure you're in the project directory first!
daphne -b 127.0.0.1 -p 8000 restaurant_system.asgi:application

# Alternative shorter version (if the above doesn't work)
daphne restaurant_system.asgi:application

# Alternative: Run without WebSocket support (admin panel real-time features won't work)
python manage.py runserver

# Database operations
python manage.py makemigrations
python manage.py migrate

# Create superuser (required for admin panel access)
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run tests
python manage.py test

# Run specific app tests
python manage.py test authentication
python manage.py test tables
python manage.py test food
python manage.py test orders
python manage.py test payment
python manage.py test admin_panel
```

### Database Configuration
The project is configured for PostgreSQL with these credentials:
- Database: `restaurant_system_db`
- User: `restaurant_user`
- Password: `WSSHLI`
- Host: `localhost`
- Port: `5432`

Create the database before running migrations:
```sql
CREATE DATABASE restaurant_system_db;
GRANT ALL PRIVILEGES ON DATABASE restaurant_system_db TO restaurant_user;
ALTER USER restaurant_user WITH SUPERUSER;
```

## Configuration

### Key Settings
- **ASGI Application**: `restaurant_system.asgi.application` (Channels enabled)
- **Channel Layers**: In-memory for development
- **Static Files**: WhiteNoise with compressed manifest storage
- **Authentication**: Custom login/logout URLs, session-based
- **Templates**: Global templates directory at project root
- **Media Files**: Served at `/media/` with local storage

### Environment Variables
- `SECRET_KEY`: Django secret key (has default for development)
- `DEBUG`: Debug mode (defaults to True)
- Database credentials are hardcoded in settings (not production-ready)

## URL Structure
- `/`: Redirects to authentication login
- `/admin/`: Django admin interface
- `/auth/`: Authentication app URLs (login, register, logout)
- `/tables/`: Table management URLs
- `/food/`: Food menu and ordering URLs
- `/orders/`: Order processing URLs
- `/payment/`: Payment handling URLs
- `/admin-panel/`: Staff dashboard and management interface

## Admin Panel Features
The admin panel (`/admin-panel/`) provides comprehensive restaurant management:

### Dashboard (`/admin-panel/`)
- Real-time order monitoring with WebSocket updates
- Daily revenue and order statistics
- Table occupancy overview
- Quick action buttons for common tasks

### Order Management (`/admin-panel/orders/`)
- Complete order history with filtering and search
- Order status updates
- Pagination for large datasets
- Export capabilities for reports

### Income Reports (`/admin-panel/income/`)
- Daily and monthly revenue reports
- Automated report generation
- Income trend analysis
- Order completion statistics

### Table Management (`/admin-panel/tables/`)
- Add/remove restaurant tables
- Real-time table status monitoring
- Table capacity management
- One-click table release functionality

### Food Management (`/admin-panel/food/`)
- Add food categories and items
- Manage food availability
- Image upload for menu items
- Price and preparation time settings

## Real-time Features
- **WebSocket Endpoint**: `ws://localhost:8000/ws/admin/orders/`
- **Real-time Order Updates**: New orders appear instantly in admin dashboard
- **Status Change Notifications**: Order status updates broadcast to admin users
- **Live Table Status**: Real-time table availability updates

## Key Models
- **Order**: Central order model with status tracking and customer relationships
- **OrderItem**: Individual items within orders with quantity and pricing
- **Table**: Restaurant table management with reservation system
- **FoodItem/FoodCategory**: Menu management with categories and items
- **Payment**: Payment processing with multiple payment methods
- **DailyReport/MonthlyReport**: Automated reporting for income tracking
- **AdminSettings**: Global restaurant configuration settings

## Development Status
Based on the codebase analysis, this appears to be a project skeleton with:
- Complete Django project structure and configuration
- Empty model files across all apps (models need to be implemented)
- Basic URL routing configured
- Template directories created but templates need implementation
- All dependencies installed and configured

The next development phase would involve implementing the actual models, views, and templates for each application.