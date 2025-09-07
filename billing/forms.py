from django import forms

class BillingForm(forms.Form):
    customer_email = forms.EmailField(label="Customer Email")
