# Deployment Guide

This guide covers different deployment options for the Restaurant Order Management System.

## Prerequisites

- Python 3.9+
- PostgreSQL database
- Redis server
- Git repository on GitHub

## Environment Variables

Set these environment variables in your deployment platform:

```bash
SECRET_KEY=your-secret-key-here
DEBUG=False
DATABASE_URL=postgres://user:password@host:port/database
REDIS_URL=redis://host:port
```

## Railway Deployment

1. **Create Railway Account**: Sign up at [railway.app](https://railway.app)

2. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

3. **Login and Initialize**:
   ```bash
   railway login
   railway init
   ```

4. **Add PostgreSQL and Redis**:
   ```bash
   railway add postgresql
   railway add redis
   ```

5. **Set Environment Variables**:
   ```bash
   railway variables set SECRET_KEY=your-secret-key
   railway variables set DEBUG=False
   railway variables set DJANGO_SETTINGS_MODULE=restaurant_system.production_settings
   ```

6. **Deploy**:
   ```bash
   railway up
   ```

## Heroku Deployment

1. **Create Heroku App**:
   ```bash
   heroku create your-app-name
   ```

2. **Add PostgreSQL and Redis**:
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   heroku addons:create heroku-redis:hobby-dev
   ```

3. **Set Environment Variables**:
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DEBUG=False
   heroku config:set DJANGO_SETTINGS_MODULE=restaurant_system.production_settings
   ```

4. **Deploy**:
   ```bash
   git push heroku main
   ```

5. **Run Migrations**:
   ```bash
   heroku run python manage.py migrate
   heroku run python manage.py createsuperuser
   ```

## Docker Deployment

1. **Build Image**:
   ```bash
   docker build -t restaurant-system .
   ```

2. **Run with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

3. **Run Migrations**:
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

## GitHub Actions CI/CD

The repository includes a comprehensive CI/CD pipeline that:

- Runs tests on every push and pull request
- Checks code quality with flake8
- Runs security checks with bandit
- Generates coverage reports
- Deploys to Railway/Heroku on main branch pushes

### Required GitHub Secrets

Add these secrets to your GitHub repository:

```
RAILWAY_TOKEN          # Railway deployment token
DJANGO_SECRET_KEY      # Django secret key
DATABASE_URL           # Production database URL
REDIS_URL             # Production Redis URL
HEROKU_API_KEY        # Heroku API key
HEROKU_APP_NAME       # Heroku app name
HEROKU_EMAIL          # Heroku account email
```

## Post-Deployment Steps

1. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

2. **Create Superuser**:
   ```bash
   python manage.py createsuperuser
   ```

3. **Set Up Tables**:
   ```bash
   python manage.py setup_tables
   ```

4. **Collect Static Files**:
   ```bash
   python manage.py collectstatic --noinput
   ```

## Monitoring and Logging

- Check application logs in your deployment platform
- Monitor database performance
- Set up health checks for the application
- Configure alerts for critical errors

## Security Considerations

- Use HTTPS in production
- Set secure headers (already configured in production_settings.py)
- Regularly update dependencies
- Use environment variables for sensitive data
- Enable database connection pooling
- Set up proper backup strategies

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Check DATABASE_URL format
   - Verify database credentials
   - Ensure database server is running

2. **Redis Connection Issues**:
   - Check REDIS_URL format
   - Verify Redis server is accessible
   - Check WebSocket functionality

3. **Static Files Not Loading**:
   - Run `python manage.py collectstatic`
   - Check WhiteNoise configuration
   - Verify STATIC_ROOT settings

4. **WebSocket Issues**:
   - Ensure Daphne is running (not just Django runserver)
   - Check Redis connection
   - Verify WebSocket routing configuration