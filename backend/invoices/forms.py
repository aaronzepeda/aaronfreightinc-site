from django import forms
from django.forms.models import fields_for_model
from datetime import datetime, timedelta
from .ocr import read_bill_of_lading
from .models import (
    Address,
    Company,
    Truck,
    Driver,
    Trip,
    Invoice,
)


DEFAULT_DRIVER = { 'first_name' : 'Aaron', 'last_name' : 'Zepeda' }
DEFAULT_INVOICING_PARTY = "Aaron Freight, Inc."
DEFAULT_INVOICED_PARTY = "Sweetener Products Company"
DEFAULT_TERMS = 30

# Create your forms here.
class BillOfLadingToTripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = (
            'trailer',
            'ship_to_address',
        )
        labels = {
            "ship_to_address": "Ship-To-Address"
        }


class BillOfLadingToInvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = (
            'rate',
            'notes',
        )

    def generate_trip(invoice_number, trailer, ship_to_address):
        truck = Truck.objects.filter(number=771).first()
        driver = Driver.objects.filter(first_name=DEFAULT_DRIVER['first_name'], last_name=DEFAULT_DRIVER['last_name']).first()
        ship_from_address = Address.objects.filter(name=DEFAULT_INVOICED_PARTY).first()

        trip = Trip(
            trip_number = invoice_number,
            truck = truck,
            trailer = trailer,
            driver = driver,
            ship_from_address = ship_from_address,
            ship_to_address = ship_to_address
        )

        return trip

    def generate_invoice(invoice_number, bill_of_lading, trip, rate, notes):

        mapped_bill_of_lading = read_bill_of_lading(bill_of_lading.file)
        trip.attachment = bill_of_lading
        trip.delivery_number = mapped_bill_of_lading['delivery_number']
        trip.delivery_date = datetime.strptime(mapped_bill_of_lading['delivery_date'], '%m/%d/%y').date()

        sales_number = mapped_bill_of_lading['sales_number']
        delivery_date = datetime.strptime(mapped_bill_of_lading['delivery_date'], '%m/%d/%y').date()
        date = delivery_date
        due_date = date + timedelta(days=DEFAULT_TERMS)

        invoicing_party = Company.objects.filter(name=DEFAULT_INVOICING_PARTY).first()
        invoiced_party = Company.objects.filter(name=DEFAULT_INVOICED_PARTY).first()

        invoice = Invoice(
            invoicing_party = invoicing_party,
            invoiced_party = invoiced_party,
            invoice_number = invoice_number,
            terms = DEFAULT_TERMS,
            date = delivery_date,
            due_date = due_date,
            sales_number = sales_number,
            trip = trip,
            rate = rate,
            notes = notes
        )

        return invoice

        

class BillOfLadingForm(forms.Form):
    bill_of_lading = forms.FileField()
    optional_invoice_number = forms.IntegerField(required=False, label="Invoice Number")