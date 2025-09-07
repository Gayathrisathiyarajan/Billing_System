# Billing System

A Django-based billing system that allows tracking of products, generating bills, calculating taxes, managing denominations, and sending invoices via email.

## 🛠️ Technology Stack  

- **Programming Language:** Python 3  
- **Framework:** Django  
- **Database:** SQLite (default) 
- **Frontend:** HTML, CSS, JavaScript (Django Templates)   
- **Version Control & Hosting:** GitHub  

## Features

1. Add products with fields:
   - Product ID
   - Name
   - Available stock
   - Unit price
   - Tax percentage
   
3. Billing Page:
   - Enter customer email.
   - Add multiple products dynamically with quantity.
   - Collect customer's paid amount.
   - Calculates subtotal, tax, grand total, and balance.
   - Determines balance denomination based on available shop denominations.
   - Generates and displays bill.
   - Sends invoice to customer through email.

4. View Previous Purchases:
   - List all previous purchases for a customer.
   - View details of each purchase.
   - If the customer email ID is already registered, a **"View Previous Purchases"** button will appear.  
   - If the customer is newly registered, this button will **not** be shown.  

## Setup Instructions

1. Clone the repository:

```bash
git clone https://github.com/Gayathrisathiyarajan/Billing_System.git
cd Billing_System
```
2. Create virtual environment & activate:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

```
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Apply migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create superuser (optional, for admin access):

```bash
python manage.py createsuperuser
```

6. Adding Products to the Database
  You can add products to the billing system using**Django shell**.
   
- Run the Django shell:

    ```bash
    python manage.py shell
    ```
- Then execute:
  
   ```bash
    from billing.models import Product
    from decimal import Decimal

    # Example products
    products = [
        {"product_code": "P1005", "name": "Eggs", "available_stock": 120, "unit_price": Decimal("6.50"), "tax_percent": Decimal("5")},
        {"product_code": "P1006", "name": "Butter", "available_stock": 50, "unit_price": Decimal("40.00"), "tax_percent": Decimal("12")},
        {"product_code": "P1007", "name": "Cheese", "available_stock": 60, "unit_price": Decimal("55.00"), "tax_percent": Decimal("18")},
        {"product_code": "P1008", "name": "Juice", "available_stock": 70, "unit_price": Decimal("35.00"), "tax_percent": Decimal("12")},
        {"product_code": "P1009", "name": "Shampoo", "available_stock": 40, "unit_price": Decimal("150.00"), "tax_percent": Decimal("18")},
    ]
    
    for p in products:
        Product.objects.create(**p)
   ```
- Exit shell:
  
   ```bash
    exit()
   ```
7. Run the Project:

```bash
python manage.py runserver
```

8. Access the app at:
```bash
http://127.0.0.1:8000/
```


---

## 👩‍💻 Author  

**Gayathri S**  
- 📧 Email: gayathrisathiyarajan@gmail.com
- 🌐 GitHub: [Gayathrisathiyarajan](https://github.com/Gayathrisathiyarajan)  
