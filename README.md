![Gardenway](images/banner.png)

# Gardenway - Backend

Welcome to the **backend** of Gardenway — an online garden store built with Django REST Framework and MySQL, deployed to Heroku, and integrated with Cloudinary for media storage.

[Live Backend](https://gardenway-11a7983dd747.herokuapp.com/)  
[Live Frontend](https://gardenway.netlify.app/) | [Frontend GitHub Repo](https://github.com/nougat-rey/gardenway_frontend)

---

## Project Purpose

This project builds a robust, production-ready e-commerce backend using modern tools and best practices.

---

## Features

✅ JWT Authentication  
✅ Cloudinary integration for product image uploads  
✅ MySQL for relational data modeling  
✅ Robust test coverage using `pytest`  
✅ Admin dashboard for product + order management  
✅ RESTful API with pagination, filtering, and custom serializers  
✅ Deployed backend on Heroku  
✅ Connected to live frontend at [gardenway.netlify.app](https://gardenway.netlify.app)

---

## Getting Started

### 1. Clone and install dependencies

```bash
git clone https://github.com/nougat-rey/gardenway.git
cd gardenway
pipenv install
pipenv shell
```

### 2. Configure environment

Create a new config file:

```bash
touch gardenway/settings/dev.py
```

Inside `dev.py`, add:

```python
DEV_SECRET_KEY = '<your-secret-key>'
DB_PASSWORD = '<your-mysql-password>'
```

You can generate a Django secret key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Set up the database

```bash
mysql -u root -p
```

Then inside MySQL shell:

```sql
CREATE DATABASE store;
USE store;
```

In your project root:

```bash
python manage.py makemigrations store
python manage.py makemigrations
python manage.py migrate
```

Create a superuser:

```bash
python manage.py createsuperuser
```

Seed the database (optional):

```bash
cd seeds
mysql -u root -p < seed.sql
```

### 4. Start the development server

```bash
python manage.py runserver
```

- API available at: `http://localhost:8000/store/`
- Admin dashboard: `http://localhost:8000/admin/`

---

## Running Tests

```bash
pytest store/tests/
```

This project uses `pytest` for testing views, models, and authentication.

---

## Deployment

Gardenway is deployed to Heroku. To deploy your own version:

1. Set environment variables (Heroku CLI or dashboard):

   - `SECRET_KEY`
   - `DB_PASSWORD`
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`

2. Run migrations and collect static files:

```bash
python manage.py migrate
python manage.py collectstatic
```

---

## Media Hosting with Cloudinary

Product images are uploaded and served via Cloudinary.

You’ll need to configure the following in your environment:

```env
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

---

## Contact

Have questions or feedback?  
Email me at: **geoffrey.nguyen9@gmail.com**

---

## Repo Overview

```bash
gardenway/
├── store/               # Core Django app (products, categories, orders, etc.)
├── seeds/               # SQL seed files for development
├── settings/            # Environment-based settings (dev, prod)
├── tests/               # Pytest tests
```

---

## Acknowledgements

- [Django REST Framework](https://www.django-rest-framework.org/)
- [Cloudinary](https://cloudinary.com/)
- [Pytest](https://docs.pytest.org/)
- [Heroku](https://www.heroku.com/)
- [Netlify](https://www.netlify.com/)
