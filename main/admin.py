from django.contrib import admin
from .models import Category, Customer, Country, Sizes, Colors, Product, ProductImage, Order, Employee, ConOrder

admin.site.register(Employee)
admin.site.register(Order)
admin.site.register(ProductImage)
admin.site.register(Colors)
admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(Country)
admin.site.register(Sizes)
admin.site.register(Category)
admin.site.register(ConOrder)

# Register your models here.
