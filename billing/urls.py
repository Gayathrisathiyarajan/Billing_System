from django.urls import path
from . import views

app_name = "billing"

urlpatterns = [
    path("", views.billing_page, name="billing_page"),
    path("generate/", views.generate_bill, name="generate_bill"),
    path("purchases/", views.purchases_list, name="purchases_list"),
    path("purchase/<int:pk>/", views.purchase_detail, name="purchase_detail"),
    path("check_previous/", views.check_previous_purchases, name="check_previous"),

]
