from django.contrib import admin
from django.contrib import admin
from .models import (
    ProductTypes,
    Manufactures,
    Products,
    ProductPictures,
)

# Register your models here.
admin.site.register([
    ProductTypes,
    Manufactures,
    Products,
    ProductPictures,
])
