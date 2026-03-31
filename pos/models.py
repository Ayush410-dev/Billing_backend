from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pos_customers')
    customer_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.customer_name


class Product(models.Model):
    CATEGORY_CHOICES = (
        ('Apparel', 'Apparel'),
        ('Footwear', 'Footwear'),
        ('General', 'General'),
        ('Supplements', 'Supplements'),
        ('Grocery', 'Grocery'),
        ('Electronics', 'Electronics'),
        ('Services', 'Services'),
        ('Automotive', 'Automotive'),
        ('Construction', 'Construction'),
        ('Cosmetics', 'Cosmetics'),
        ('Furniture', 'Furniture'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pos_products')
    product_name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='General')
    price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='pos_products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product_name} ({self.sku})"


class PosSale(models.Model):
    PAYMENT_CHOICES = (
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('UPI', 'UPI'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Mixed', 'Mixed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pos_sales')
    sale_no = models.CharField(max_length=100, unique=True)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pos_sales'
    )

    payment_method = models.CharField(max_length=30, choices=PAYMENT_CHOICES, default='Cash')
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    amount_received = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    change_due = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sale_no


class PosSaleItem(models.Model):
    sale = models.ForeignKey(PosSale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sale_items')

    product_name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100)
    batch = models.CharField(max_length=100, blank=True, null=True)

    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"{self.sale.sale_no} - {self.product_name}"