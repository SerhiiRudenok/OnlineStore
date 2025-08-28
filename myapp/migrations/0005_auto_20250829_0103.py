from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import migrations, models
from django.conf import settings

class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0004_remove_product_slug_product_favorites_order_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('text', models.TextField()),
                ('rating', models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])),
                ('product', models.ForeignKey(on_delete=models.CASCADE, related_name='comments', to='myapp.Product')),
                ('user', models.ForeignKey(on_delete=models.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={'unique_together': {('product', 'user')}},
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('total_price', models.DecimalField(max_digits=10, decimal_places=2)),
                ('user', models.ForeignKey(on_delete=models.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.PositiveIntegerField()),
                ('price', models.DecimalField(max_digits=10, decimal_places=2)),
                ('order', models.ForeignKey(on_delete=models.CASCADE, related_name='items', to='myapp.Order')),
                ('product', models.ForeignKey(on_delete=models.SET_NULL, null=True, to='myapp.Product')),
            ],
        ),
    ]