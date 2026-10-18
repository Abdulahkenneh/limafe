# Assuming the project structure with multiple apps as previously mentioned: accounts, content, events, donations, communications, analytics.
# I'll provide admin.py for each relevant app, and a signals.py where necessary.
# For signals, we'll use them to handle post-save actions like email sending, to decouple from model save methods.
# Remove the email logic from model save() methods and move to signals.
# Also, for automated reminders (e.g., 24h before event), we'd need a task scheduler like Celery, but for now, I'll note it.
# For alerts (suspicious activity), that could be via signals on login failures, etc.

# First, update models to remove email logic from save():
# In Booking model: remove the save() override or just super().save() without email.
# In Donation: same, remove email from save().

# signals.py (place in each app or a core app, but for simplicity, show per app)

# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser  # Assuming CustomUser in accounts

# No specific signals for users yet, but could add for new user welcome email if needed.

# events/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Booking

@receiver(post_save, sender=Booking)
def send_booking_confirmation(sender, instance, created, **kwargs):
    if created:
        send_mail(
            'Event Booking Confirmation',
            f'Your verification code: {instance.verification_code}',
            settings.DEFAULT_FROM_EMAIL,
            [instance.user.email],
        )

# For event reminders: This would be better as a periodic task.
# Example: Use Celery beat to check events starting in 24h and send reminders to bookings.
# But for illustration, if we want a signal on event creation/update, but that's not ideal for timed actions.

# donations/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Donation

@receiver(post_save, sender=Donation)
def send_donation_receipt(sender, instance, created, **kwargs):
    if created and instance.user and not instance.receipt_sent:
        send_mail(
            'Donation Receipt',
            f'Thank you for your donation of {instance.amount}!',
            settings.DEFAULT_FROM_EMAIL,
            [instance.user.email],
        )
        instance.receipt_sent = True
        instance.save(update_fields=['receipt_sent'])

# For failed logins/alerts: Use Django's user_logged_in, user_login_failed signals.
# Example in accounts/signals.py
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver

@receiver(user_login_failed)
def handle_failed_login(sender, credentials, request, **kwargs):
    # Log or send alert email to admin
    send_mail(
        'Suspicious Login Attempt',
        f'Failed login for {credentials.get("username")} from IP {request.META.get("REMOTE_ADDR")}',
        settings.DEFAULT_FROM_EMAIL,
        [settings.ADMIN_EMAIL],  # Assume defined in settings
    )