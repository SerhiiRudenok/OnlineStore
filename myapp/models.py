from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.validators import RegexValidator



# --- Категорія товара
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# --- Товар
class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='myapp/images/', blank=True, default='myapp/images/no-image.jpg')
    is_active = models.BooleanField(default=True)
    favorites = models.ManyToManyField(User, related_name='favorite_product', blank=True)

    def __str__(self):
        return self.name


# --- Відгук
class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', null=True)
    date = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        unique_together = ('product', 'user')

    def __str__(self):
        return f'Відгук {self.user.username} до "{self.product.name}"'


# --- Кошик
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')

    def __str__(self):
        return f'Кошик {self.user.username}'

    def get_total_price(self):
        return sum(item.product.price * item.quantity for item in self.items.all() if item.product)


# --- Товар у кошику
class BookingItem(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} × {self.product.name}'


# --- Замовлення
class Order(models.Model):
    DELIVERY_CHOICES = [
        ('nova_poshta_branch', 'Самовивіз з Нової Пошти'),
        ('nova_poshta_postomat', 'Самовивіз з поштоматів Нової Пошти'),
        ('meest_branch', 'Самовивіз з Meest ПОШТА'),
        ('ukrposhta_branch', 'Самовивіз з УКРПОШТИ'),
        ('meest_courier', 'Курʼєр Meest ПОШТА'),
        ('nova_poshta_courier', 'Курʼєр Нової Пошти'),
    ]

    PAYMENT_CHOICES = [
        ('card', 'Оплата картою Visa/MasterCard'),
        ('cash_on_delivery', 'Оплата під час отримання товару'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    # доставка та оплата
    delivery_method = models.CharField(max_length=30, choices=DELIVERY_CHOICES, default='nova_poshta_branch')
    delivery_address = models.CharField(max_length=255, default='Потребує уточнення')
    payment_method = models.CharField(max_length=30, choices=PAYMENT_CHOICES, default='cash_on_delivery')

    def __str__(self):
        return f"Замовлення № {self.id} від {self.user.username}"

    def clean(self):
        restricted_delivery = [
            'nova_poshta_postomat',
        ]
        if self.delivery_method in restricted_delivery and self.payment_method == 'cash_on_delivery':
            raise ValidationError("Цей спосіб доставки не підтримує оплату під час отримання товару")


# --- Товар в замовленні
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)


# --- Профіль моделі User
# --- мобільний телефон
phone_validator = RegexValidator(
    regex=r'^\+380\d{9}$',
    message="Номер телефону має бути у форматі +380XXXXXXXXX"
)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(
        max_length=13,
        blank=True,
        validators=[phone_validator]
    )

    def __str__(self):
        return f"Профіль {self.user.username}"


# --- Сигнал Менеджеру про нове Замовлення
class OrderNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_notifications')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Сповіщення для {self.user.username} про замовлення № {self.order.id}"

    def mark_as_read(self):
        self.is_read = True
        self.save()

