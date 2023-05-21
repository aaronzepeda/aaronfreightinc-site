from django.urls import path
from . import views

app_name = 'invoices'
urlpatterns = [
    path("", views.index, name="index"),
    path("generate/", views.generate, name="generate"),
    path("pdf/<int:invoice_number>", views.view_invoice_as_pdf, name="view_invoice_as_pdf"),
]