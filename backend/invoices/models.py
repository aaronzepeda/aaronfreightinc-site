import re
from django.db import models
from phonenumber_field.modelfields import PhoneNumber, PhoneNumberField
from .utility import add_leading_zeros



class Address(models.Model):
    name = models.CharField(max_length=256, default='Source Bakery', blank=True)
    address = models.CharField(max_length=128, default=' 8601 Jefferson Street #101', blank=True)
    city = models.CharField(max_length=128, default='Tolleson', blank=True)
    state = models.CharField(max_length=2, default='AZ', blank=True)
    zip = models.CharField(max_length=5, default='85353', blank=True)
    zip_extension = models.CharField(max_length=5, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "addresses"
        
    def __str__(self):
        return self.address + ', ' +  self.city + ', ' +  self.state + ' ' + self.zip + " | " + self.name

    def get_full_address(self):
        address = self.address + ', ' +  self.city + ', ' +  self.state + ' ' + self.zip
        return address
    
    
    

class Company(models.Model):
    name = models.CharField(max_length=256, default='Aaron Trucking, Inc.', blank=True)
    brand = models.ImageField(upload_to='companies/brands')
    phone = PhoneNumberField(null=False, blank=False, unique=True)
    phone_extension = models.CharField(max_length=10, blank=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='housing_companies')
    billing_address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='billing_companies')
    email = models.EmailField(max_length=254)

    class Meta:
        verbose_name_plural = "companies"

    def __str__(self):
        return self.name

class Truck(models.Model):
    number = models.CharField(max_length=256, default='771')

    def __str__(self):
        return self.number

class Trailer(models.Model):
    number = models.CharField(max_length=256, default='7847X')

    def __str__(self):
        return self.number

class Driver(models.Model):
    first_name = models.CharField(max_length=256, default='Aaron')
    last_name = models.CharField(max_length=256, default='Zepeda')

    def __str__(self):
        return self.first_name + " " + self.last_name

class Trip(models.Model):
    trip_number = models.PositiveIntegerField(unique=True)
    delivery_date = models.DateField(auto_now_add=False, help_text="Automatically filled in")
    delivery_number = models.PositiveIntegerField()
    truck = models.ForeignKey(Truck, on_delete=models.CASCADE, related_name='trips')
    trailer = models.ForeignKey(Trailer, on_delete=models.CASCADE, related_name='trips')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='trips')
    ship_from_address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='shipped_from_invoices')
    ship_to_address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='shipped_to_invoices')
    attachment = models.FileField(upload_to='trips/attachments/')

    def __str__(self):
        return "TRIP #" + str(self.trip_number)

class Invoice(models.Model):
    TERMS_CHOICE = (
        (7, "Net 7"),
        (15, "Net 15"),
        (30, "Net 30"),
        (60, "Net 60"),
        (90, "Net 90"),
        (120, "Net 120"),
    )

    invoicing_party = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='invoicing_invoices')
    invoiced_party = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='invoiced_invoices')
    invoice_number = models.PositiveIntegerField(unique=True)
    terms = models.IntegerField(choices=TERMS_CHOICE, default=30)
    date = models.DateField(auto_now_add=False, help_text="Automatically filled in")
    due_date = models.DateField(auto_now_add=False, help_text="Automatically filled in")
    sales_number = models.PositiveIntegerField()
    trip = models.OneToOneField(Trip, on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=7, decimal_places=2)
    notes = models.TextField(blank=True)

    def __str__(self):
        return "INVOICE #" + str(self.invoice_number)

    def get_leading_zeros_invoice_number(self):
        LEADING_ZEROS = 6
        return add_leading_zeros(self.invoice_number, LEADING_ZEROS)
    
    def get_pdf_name(self):
        regex = re.compile('[^a-zA-Z]')
        clean_name = regex.sub('', self.invoicing_party.name).upper() + "_Invoice_" + self.get_leading_zeros_invoice_number()
        return clean_name

    def create_object_from_form(request):
        invoice_number = self.cleaned_data["invoice_number"]
        print(invoice_number)
