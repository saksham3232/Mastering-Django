from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from firstapp.models import Notification


def send_order_status_email(order):
    subject = f"Your Order #{order.order_id} Status Updated"
    recipient = [order.user.email]
    context = {
        'user': order.user.name,
        'order_id': order.order_id,
        'status': order.get_status_display(),  # human-readable status
        'date': order.datetime_of_payment.strftime('%B %d, %Y'),
    }
    html_message = render_to_string('firstapp/order_status_update.html', context)
    plain_message = f"Your order #{order.order_id} status has been updated to '{order.get_status_display()}'."  # human-readable

    send_mail(subject, plain_message, settings.EMAIL_HOST_USER, recipient, html_message=html_message)


def create_in_app_notification(order):
    Notification.objects.create(
        user=order.user,
        message=f"Order #{order.order_id} status updated to '{order.get_status_display()}'."
    )


def handle_order_status_change(order, new_status):
    if order.status == 5:  # 🚫 Do not overwrite cancelled orders
        return False

    if order.status != new_status:
        order.status = new_status
        order.save()
        send_order_status_email(order)
        create_in_app_notification(order)
        return True  # Status changed
    return False  # No change
