from django.contrib import admin
from .models import (
    Address,
    Company,
    Truck,
    Trailer,
    Driver,
    Trip,
    Invoice
)

admin.site.register(Address)
admin.site.register(Company)
admin.site.register(Truck)
admin.site.register(Trailer)
admin.site.register(Driver)
admin.site.register(Trip)
admin.site.register(Invoice)
