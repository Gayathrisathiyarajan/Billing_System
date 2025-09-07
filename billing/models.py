from django.db import models
from decimal import Decimal


class Customer(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email


class Product(models.Model):
    product_code = models.CharField(max_length=50, unique=True, db_column='product_id')
    name = models.CharField(max_length=200)
    available_stock = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))

    def __str__(self):
        return f"{self.product_code} - {self.name}"


class Denomination(models.Model):
    value = models.PositiveIntegerField(unique=True)
    available_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"₹{self.value} x {self.available_count}"


class Purchase(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    tax_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    change_due = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    change_breakdown = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice {self.id} - {self.customer.email}"

    def calculate_totals(self):
        subtotal = Decimal("0.00")
        tax_total = Decimal("0.00")

        for item in self.items.all():
            subtotal += item.calculate_line_total()
            tax_total += (item.calculate_line_total() * (item.product.tax_percent / Decimal("100"))).quantize(Decimal("0.01"))

        self.subtotal = subtotal.quantize(Decimal("0.01"))
        self.tax_total = tax_total.quantize(Decimal("0.01"))
        self.grand_total = (self.subtotal + self.tax_total).quantize(Decimal("0.01"))

        return self.grand_total


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.product.product_code} x {self.quantity}"

    def calculate_line_total(self):
        return (self.unit_price * self.quantity).quantize(Decimal("0.01"))