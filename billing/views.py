from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from decimal import Decimal
from .models import Product, Denomination, Purchase, PurchaseItem, Customer
import threading
from django.http import JsonResponse
from math import floor, ceil


def billing_page(request):
    try:
        products = Product.objects.all()
        required_values = [500, 200, 50, 20, 10, 5, 1]
        denominations = Denomination.objects.filter(value__in=required_values).order_by("-value")
    except Exception as e:
        print(f"Error in billing_page: {e}")
        products = []
        denominations = []
    return render(request, "billing.html", {"products": products, "denominations": denominations})


def calculate_change(change_due, denominations):
    remaining = change_due
    breakdown = {}
    for d in denominations:
        if remaining <= 0:
            break
        count_needed = int(remaining // d.value)
        use = min(count_needed, d.available_count)
        if use > 0:
            breakdown[str(d.value)] = use
            remaining -= d.value * use
    if remaining > 0:
        return None
    return breakdown


def send_invoice_email(purchase_id):
    purchase = Purchase.objects.get(id=purchase_id)
    context = {"purchase": purchase, "items": purchase.items.all()}
    html_content = render_to_string("email_invoice.html", context)
    email = EmailMessage(
        subject=f"Invoice #{purchase.id}",
        body=html_content,
        to=[purchase.customer.email],
    )
    email.content_subtype = "html"
    email.send()


def generate_bill(request):
    purchase = None
    rows = []
    breakdown = {}
    try:
        if request.method != "POST":
            return HttpResponseBadRequest("Invalid request")

        email = request.POST.get("customer_email")
        paid_amount = Decimal(request.POST.get("paid_amount", "0"))
        customer, _ = Customer.objects.get_or_create(email=email)
        product_ids = request.POST.getlist("product_id[]")
        quantities = request.POST.getlist("quantity[]")

        if not product_ids:
            return HttpResponseBadRequest("No products provided")

        purchase = Purchase.objects.create(customer=customer, paid_amount=paid_amount)

        subtotal = Decimal("0.00")
        tax_total = Decimal("0.00")

        # loop products
        for pid, qty in zip(product_ids, quantities):
            product = get_object_or_404(Product, product_code=pid)
            qty = int(qty)

            if product.available_stock < qty:
                return HttpResponseBadRequest(f"Not enough stock for {product.name}")

            line_total = (product.unit_price * qty).quantize(Decimal("0.01"))
            tax_amount = (line_total * (product.tax_percent / Decimal("100"))).quantize(Decimal("0.01"))
            total_with_tax = (line_total + tax_amount).quantize(Decimal("0.01"))

            PurchaseItem.objects.create(purchase=purchase, product=product, quantity=qty, unit_price=product.unit_price, line_total=line_total,)

            rows.append({
                "product_code": product.product_code,
                "name": product.name,
                "unit_price": product.unit_price,
                "quantity": qty,
                "line_total": line_total,
                "tax_percent": product.tax_percent,
                "tax_amount": tax_amount,
                "total_with_tax": total_with_tax,
            })

            subtotal += line_total
            tax_total += tax_amount

            product.available_stock -= qty
            product.save()

        # calculate grand total with nearest rupee rounding
        grand_total = subtotal + tax_total
        paisa = grand_total - int(grand_total)
        if paisa >= Decimal("0.50"):
            grand_total = Decimal(ceil(grand_total))
        else:
            grand_total = Decimal(floor(grand_total))

        purchase.subtotal = subtotal
        purchase.tax_total = tax_total
        purchase.grand_total = grand_total

        # calculate change due
        change_due = int(paid_amount - grand_total)
        purchase.change_due = change_due if change_due >= 0 else 0

        # calculate denomination breakdown
        denominations = Denomination.objects.all().order_by("-value")
        breakdown = calculate_change(change_due, denominations)

        if breakdown:
            purchase.change_breakdown = breakdown
            for val, cnt in breakdown.items():
                d = Denomination.objects.get(value=int(val))
                d.available_count -= cnt
                d.save()

        purchase.save()
        threading.Thread(target=send_invoice_email, args=(purchase.id,)).start()

    except Exception as e:
        print(f"Error in generate_bill: {e}")
        return HttpResponseBadRequest(f"Error generating bill: {e}")

    return render(request, "bill.html", {"purchase": purchase, "rows": rows, "breakdown": breakdown})


def purchases_list(request):
    email = None
    if request.method == "POST":
        email = request.POST.get("email")
    purchases = []
    if email:
        customer = Customer.objects.filter(email=email).first()
        if customer:
            purchases = Purchase.objects.filter(customer=customer).order_by("-created_at")
    return render(request, "purchases_list.html", {"purchases": purchases, "email": email})


def purchase_detail(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    return render(request, "purchase_detail.html", {"purchase": purchase, "items": purchase.items.all()})


def check_previous_purchases(request):
    try:
        email = request.GET.get("email")
        if not email:
            return JsonResponse({"exists": False})
        customer = Customer.objects.filter(email=email).first()
        if customer and Purchase.objects.filter(customer=customer).exists():
            return JsonResponse({"exists": True})
        return JsonResponse({"exists": False})
    except Exception as e:
        print(f"Error in check_previous_purchases: {e}")
    return JsonResponse({"exists": False})