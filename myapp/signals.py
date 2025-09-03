from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import localtime
from .models import Order, OrderNotification
from django.contrib.auth.models import User

@receiver(post_save, sender=Order)
def notify_manager_on_order(sender, instance, created, **kwargs):
    if created:
        managers = User.objects.filter(groups__name='Manager')
        local_date = localtime(instance.date)
        formatted_date = local_date.strftime('%d.%m.%Y, %H:%M')

        for manager in managers:
            OrderNotification.objects.create(
                user=manager,
                order=instance,
                message=f"Нове замовлення № {instance.id} від {formatted_date}"
            )