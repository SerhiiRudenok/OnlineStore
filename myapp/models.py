from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='myapp/images/', blank=False, default='myapp/images/image.jpg')
    is_active = models.BooleanField(default=True)

    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name



