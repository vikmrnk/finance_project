# Finance Manager

A comprehensive personal finance management web application built with Django. This application allows users to track their income, expenses, budgets, and financial goals.

## Features

- **Dashboard**: A visual overview of your financial health with key metrics and charts
- **Transaction Management**: Track income and expenses with flexible categorization
- **Multiple Accounts**: Support for various account types (checking, savings, credit cards, etc.)
- **Budgeting**: Create and track budgets by category with real-time progress monitoring
- **Analytics**: Detailed financial insights with interactive charts and date filtering
- **Debt Management**: Track loans, credit cards, and other liabilities
- **Subscription Tracking**: Monitor recurring expenses and subscription renewals
- **Category Management**: Customize expense and income categories with icons
- **Responsive Design**: Optimized for both desktop and mobile devices
- **Multilingual Support**: Interface available in Ukrainian and English

## Technologies Used

- **Backend**: Django, Python
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Data Visualization**: Chart.js
- **Icons**: Font Awesome
- **Database**: SQLite (development) / PostgreSQL (production)

## Installation and Setup

1. Clone the repository:
   ```
   git clone
   cd finance_project
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```
   python manage.py migrate
   ```

5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

## Usage

1. Register a new account or login with existing credentials
2. Set up your accounts (checking, savings, credit cards, etc.)
3. Add your income sources and recurring expenses
4. Create budgets for different expense categories
5. Track your transactions regularly
6. Use the analytics page to gain insights into your financial health

## Deploy on Render (Free Tier)

1. Create a **PostgreSQL** database in Render and copy the `External Database URL`.
2. Create a **Web Service** from this repository.
3. Set:
   - Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - Start command: `gunicorn FinanceManager.wsgi:application`
4. Add environment variables in Render:
   - `DJANGO_SECRET_KEY` = a long random string
   - `DJANGO_DEBUG` = `False`
   - `DJANGO_ALLOWED_HOSTS` = `<your-service>.onrender.com`
   - `DJANGO_CSRF_TRUSTED_ORIGINS` = `https://<your-service>.onrender.com`
   - `DATABASE_URL` = PostgreSQL URL from Render
5. Redeploy the service.

## Project Structure

- **fin_manager/**: The main Django app containing models, views, and templates
- **FinanceManager/**: The Django project settings and configuration
- **templates/**: HTML templates organized by feature
- **static/**: CSS, JavaScript, and image files for the frontend

## Author

Viktoriia Kamarenko - [https://github.com/vikmrnk](https://github.com/vikmrnk)
