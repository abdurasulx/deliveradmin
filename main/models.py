from django.db import models
from django.contrib.auth.models import User
from .func import  transliterate_to_krill


class Category(models.Model):
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class DeleviryType(models.TextChoices):
    STANDART = 'standart', 'STANDART'
    INDUVIDIAL = 'induvidial', 'INDUVIDIAL'
class OrderStatus(models.TextChoices):
    NEW = 'new', 'Yangi'
    PENDING = 'pending', 'Kutilmoqda'
    PROCESSING = 'processing', 'Jarayonda'
    OUT_FOR_DELIVERY = 'out_for_delivery', 'Yetkazib berilmoqda'
    DELIVERED = 'delivered', 'Yetkazildi'
    CANCELLED = 'cancelled', 'Bekor qilingan'

class Order(models.Model):
    store = models.ForeignKey(User, on_delete=models.CASCADE,blank=True, null=True)
    customer = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='customer_orders')
    delivery_person = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='delivery_orders')

    customer_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, null=True, blank=True) 
    region = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True , related_name='region')  
    district = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True , related_name='district')
    deleviry_type = models.CharField(max_length=20, choices=DeleviryType.choices, blank=True)
    address = models.TextField(blank=True)
    # Location coordinates
    latitude = models.DecimalField(max_digits=20, decimal_places=16, null=True, blank=True)
    longitude = models.DecimalField(max_digits=20, decimal_places=16, null=True, blank=True)

    status = models.CharField(max_length=50, default=OrderStatus.NEW, choices=OrderStatus.choices)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    delivery_person_comment = models.TextField(blank=True)
    deleviry_paid = models.BooleanField(default=False)
    delevery_date = models.DateField(null=True, blank=True)
    delevery_time = models.TimeField(null=True, blank=True)
    
class Customer(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)



class Country(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Sizes(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Colors(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
class Product(models.Model):
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.SET_NULL)
    count = models.IntegerField(null=True, blank=True)
    sizes = models.ManyToManyField(Sizes, null=True, blank=True)
    colors = models.ManyToManyField(Colors, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    name_krill = models.CharField(max_length=150, null=True, blank=True)
    description_krill = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
            if self.name and not self.name_krill:
                self.name_krill = transliterate_to_krill(self.name)
            if self.description and not self.description_krill:
                self.description_krill = transliterate_to_krill(self.description)
            super().save(*args, **kwargs)

    def __str__(self):
        
        return self.name
    
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    color = models.ForeignKey(Colors, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='product_images/')
    created_at = models.DateTimeField(auto_now_add=True)


class Employee(models.Model):
    ROLE_CHOICES = [
        ('manager', 'Boshqaruvchi'),
        ('supplier', 'Yetkazib beruvchi'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='supplier')
    is_activ = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    password = models.CharField(max_length=128,null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.get_role_display()})"  
    
class ConOrder(models.Model):
    id=models.AutoField(primary_key=True)
    orderlist = models.ForeignKey(Order, on_delete=models.CASCADE)
    client = models.ForeignKey(Customer, on_delete=models.CASCADE)
    delivery_address = models.TextField()
    status = models.CharField(max_length=50, default='pending')
    deliver=models.ForeignKey(Employee, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
class OrderItem(models.Model):
        order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
        product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
        quantity = models.IntegerField(default=1)
        price = models.DecimalField(max_digits=10, decimal_places=2)
        total_price = models.DecimalField(max_digits=10, decimal_places=2)
        created_at = models.DateTimeField(auto_now_add=True)