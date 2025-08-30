# Generated manually on 2025-08-30

from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_booking_bookingitem'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='favorites',
            field=models.ManyToManyField(
                to=settings.AUTH_USER_MODEL,
                related_name='favorite_product',
                blank=True
            ),
        ),
    ]