# WildSport — Mini E-Commerce Platform

**From Stadium to Summit.**

A full-stack e-commerce web application built with **Django**, **Django REST Framework**, and **Bootstrap**, inspired by sports & outdoor retail platforms like Decathlon. Built as part of a Python Django Developer assignment.

**Live Demo:** [https://wildsport.onrender.com/](https://wildsport.onrender.com/)

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Database Design](#database-design)
- [REST API Reference](#rest-api-reference)
- [Admin Dashboard](#admin-dashboard)
- [Setup Instructions](#setup-instructions)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)

---

## Features

- User Registration, Login, Logout (Token Authentication)
- Multiple saved addresses per user
- Category management (with subcategory support)
- Product catalog with multiple images, brand, size/variant support
- Product search, filtering (category, brand, price range), sorting, and pagination
- Shopping cart (add / update / remove / clear, size-aware)
- Checkout with Cash on Delivery
- Order history and order detail/cancel
- User profile management
- Custom admin dashboard (separate from Django's built-in `/admin/`)
- Responsive UI built with Bootstrap
- Media storage via Cloudinary, static files via WhiteNoise
- Deployed on Render

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Django 4.2, Django REST Framework |
| Database | PostgreSQL (production) / MySQL / SQLite (local, via `dj-database-url`) |
| Authentication | DRF Token Authentication |
| Media Storage | Cloudinary |
| Static Files | WhiteNoise |
| Frontend | Django Templates + Bootstrap |
| Deployment | Render (Gunicorn) |

---

## Project Structure

```
wildsport/
├── accounts/          # User auth, profile, addresses (API)
├── catalog/            # Category, Product, ProductVariant, ProductImage (API)
├── cart/                # Cart, CartItem (API)
├── orders/              # Order, OrderItem (API)
├── dashboard/           # Custom admin panel (staff-only, template-based)
├── pages/                # Customer-facing frontend views (templates)
├── templates/            # HTML templates (home, product listing, cart, checkout, etc.)
├── static/                # CSS, JS, images
├── wildsport_core/         # Project settings, root urls
├── build.sh                 # Render build script
├── requirements.txt
└── manage.py
```

The project is split into focused apps rather than one monolithic app — each app owns its own models, serializers, views, and URLs, which keeps the codebase modular and easy to explain module-by-module.

---

## Database Design

### Entity Overview

```
User (Django built-in)
 ├── UserProfile (1:1)      → phone, address, city, state, pincode, profile_image
 ├── Address (1:M)          → multiple saved addresses, one marked default
 ├── Cart (1:1)
 │     └── CartItem (1:M)   → product, quantity, selected_size
 └── Order (1:M)
       └── OrderItem (1:M)  → product, quantity, price_at_purchase, selected_size

Category (self-referencing via `parent` → supports subcategories)
 └── Product (M:M with Category)
       ├── ProductImage (1:M)
       └── ProductVariant (1:M)  → size-wise stock (S/M/L/XL or shoe sizes)
```

### Key Design Decisions

- **`UserProfile`** is linked to Django's built-in `User` via `OneToOneField` — authentication itself is fully handled by Django, and extra profile data is kept separate.
- **`Address`** is a separate model (not merged into `UserProfile`) so a user can save multiple delivery addresses and mark one as default.
- **`Product.categories`** is a **ManyToManyField** — a product can belong to more than one category (e.g. a jacket could sit under both "Men" and "Winter Wear").
- **`Category.parent`** is a self-referencing `ForeignKey`, enabling subcategories without a separate table.
- **`ProductVariant`** stores per-size stock (e.g. size `M` has 10 in stock, size `L` has 3), separate from the product's overall `stock` field — needed because clothing/shoes are sold in specific sizes.
- **`CartItem`** has `unique_together = ('cart', 'product', 'selected_size')` — the same product in a different size is treated as a separate cart line, but re-adding the same product+size updates quantity instead of duplicating.
- **`OrderItem.price_at_purchase`** stores a *copy* of the price at the time of purchase (not a live reference to `Product.price`), so order history stays accurate even if the product's price changes later.
- **`OrderItem.product`** uses `on_delete=models.SET_NULL` — if a product is deleted later, past orders remain intact instead of being deleted.
- **`Order.order_number`** is auto-generated using a UUID (e.g. `WS4F9A2B1C3D`) for a clean, unique, customer-facing order reference.

---

## REST API Reference

Base URL (local): `http://127.0.0.1:8000/api/`

### Authentication — `/api/auth/`

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| POST | `/api/auth/register/` | No | Register a new user, returns auth token |
| POST | `/api/auth/login/` | No | Login, returns auth token |
| POST | `/api/auth/logout/` | Yes | Deletes current token (logout) |
| GET / PUT | `/api/auth/profile/` | Yes | View / update profile |
| GET / POST | `/api/auth/addresses/` | Yes | List / add saved addresses |
| DELETE | `/api/auth/addresses/<id>/` | Yes | Delete a saved address |

### Categories — `/api/`

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| GET | `/api/categories/` | No | List active categories |
| POST | `/api/categories/` | Admin | Create category |
| GET | `/api/categories/<slug>/` | No | Category detail |
| PUT / PATCH | `/api/categories/<slug>/` | Admin | Update category |
| DELETE | `/api/categories/<slug>/` | Admin | Delete category |

### Products — `/api/`

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| GET | `/api/products/` | No | List products — supports filters below |
| POST | `/api/products/` | Admin | Create product |
| GET | `/api/products/<slug>/` | No | Product detail |
| PUT / PATCH | `/api/products/<slug>/` | Admin | Update product |
| DELETE | `/api/products/<slug>/` | Admin | Delete product |
| POST | `/api/products/<slug>/upload-image/` | Admin | Upload an additional product image |

**Product list query parameters:**

| Param | Example | Description |
|---|---|---|
| `search` | `?search=shoes` | Search by product name |
| `category` | `?category=running` | Filter by category slug |
| `brand` | `?brand=nike` | Filter by brand |
| `min_price` / `max_price` | `?min_price=500&max_price=2000` | Price range filter |
| `sort` | `?sort=price_low` | `price_low`, `price_high`, `newest`, `popularity` |
| `page` | `?page=2` | Pagination (12 products per page) |

### Cart — `/api/cart/` *(auth required for all)*

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/cart/` | View current user's cart |
| POST | `/api/cart/add/` | Add item to cart |
| PUT | `/api/cart/update/<item_id>/` | Update item quantity |
| DELETE | `/api/cart/remove/<item_id>/` | Remove item from cart |
| DELETE | `/api/cart/clear/` | Clear entire cart |

### Orders — `/api/orders/` *(auth required for all)*

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/orders/checkout/` | Place order (Cash on Delivery) |
| GET | `/api/orders/` | List logged-in user's orders |
| GET | `/api/orders/<order_id>/` | Order detail |
| PUT | `/api/orders/<order_id>/cancel/` | Cancel an order |

**Authentication note:** All protected endpoints use DRF Token Authentication. Pass the token in the request header as:
```
Authorization: Token <your_token_here>
```

---

## Admin Dashboard

WildSport ships with a **custom staff-only admin dashboard** (built with Django views + templates, not the default Django admin) available at:

```
/dashboard/
```

| Route | Description |
|---|---|
| `/dashboard/login/` | Staff login |
| `/dashboard/` | Dashboard home (totals: products, categories, orders) |
| `/dashboard/categories/` | Category list / add / edit / delete |
| `/dashboard/products/` | Product list / add / edit / delete (with image management) |
| `/dashboard/orders/` | Order list and detail (status updates) |

Only users with `is_staff=True` can log in here. Django's default `/admin/` is also available for quick data inspection during development.

### Live Demo Admin Credentials

To review the admin dashboard on the live deployment ([https://wildsport.onrender.com/dashboard/](https://wildsport.onrender.com/dashboard/)), use:

**Username: `test11`**
**Password: `test@123`**

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Raj-Misal1105/wildsport.git
cd wildsport
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the project root (see [Environment Variables](#environment-variables) below for the full list).

### 5. Switch the database config for local development (MySQL / XAMPP)

By default, `wildsport_core/settings.py` is set up for **production** (Render), where the database is read from a `DATABASE_URL` env var via `dj_database_url`, falling back to SQLite if that's not set:

```python
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}
```

To run locally against **MySQL (e.g. via XAMPP)** instead, open `wildsport_core/settings.py` and swap the two blocks:

- **Comment out** the `dj_database_url` block above (the one currently active)
- **Uncomment** the MySQL block below it and fill in your own DB name / port:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'wildsport_db',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3307',
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    }
}
```

Similarly, near the top of the file, for local development:

- **Comment out** the current active line:
  ```python
  SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-sydcalxwvpc&v_!i&y24l2-ht$-wz=gu4qm0deg7*q)p2kr=0r')
  ...
  ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')
  ```
- **Uncomment** the simpler local-dev version:
  ```python
  # ALLOWED_HOSTS = ["*"]
  ```

> These two settings (`DATABASES` and `ALLOWED_HOSTS`/`SECRET_KEY`) are written to support **both** local MySQL development and Render production deployment side by side — only one version of each should be active at a time depending on where you're running the project.

### 6. Run migrations

```bash
python manage.py migrate
```

### 7. Create a superuser (for admin/dashboard access)

```bash
python manage.py createsuperuser
```

### 8. Run the development server

```bash
python manage.py runserver
```

Visit:
- Website: `http://127.0.0.1:8000/`
- Custom Admin Dashboard: `http://127.0.0.1:8000/dashboard/`
- Django Admin: `http://127.0.0.1:8000/admin/`

---

## Environment Variables

Create a `.env` file in the project root with the following keys (values are yours, do **not** commit this file):

```env
SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database (leave unset to fall back to local SQLite)
DATABASE_URL=

# Cloudinary (media storage)
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

# Auto-create a superuser on deploy (optional, used by build.sh)
DJANGO_SUPERUSER_USERNAME=
DJANGO_SUPERUSER_EMAIL=
DJANGO_SUPERUSER_PASSWORD=
```

> `.env` is already excluded via `.gitignore` and should never be committed with real values.

---

## Deployment

The project is deployed on **Render** using `build.sh`:

```bash
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py create_admin
```

- Static files are served via **WhiteNoise**.
- Media (product images, category icons, profile pictures) is stored on **Cloudinary**.
- `create_admin` is a custom management command that creates a superuser automatically from `DJANGO_SUPERUSER_*` environment variables on first deploy (skips if one already exists).

**Live URL:** [https://wildsport.onrender.com/](https://wildsport.onrender.com/)
