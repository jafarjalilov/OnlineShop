from celery import task
from django.core.mail import send_mail
from .models import Order

@task
def order_created(order_id):
    """
    Task to send an email notification when an order is successfully created. 
    """
    order = Order.objects.get(id=order_id)
    subject = f'order nr. {order.id}'
    message = f"Dear {order.first_name}, \n\n You have successfully placed an order. Your order id is {order.id}."
    mail_sent = send_mail(subject, message, 'jalilov.jafar7997@gmail.com', [order.email])

    return mail_sent
