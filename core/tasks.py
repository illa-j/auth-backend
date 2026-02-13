from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from core.models import EmailVerificationToken, PasswordChangeToken


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 10},
    retry_backoff=True,
)
def send_verification_email(self, verify_link, user_email):
    send_mail(
        subject="Verify your email",
        message=f"Click to verify: {verify_link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
    )


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 10},
    retry_backoff=True,
)
def send_password_change_confirmation_email(self, confirm_link, user_email):
    send_mail(
        subject="Confirm password change",
        message=f"Click to confirm: {confirm_link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
    )


@shared_task
def cleanup_expired_tokens_and_not_verified_users(self):
    now = timezone.now()
    email_verification_tokens = EmailVerificationToken.objects.filter(created_at__lt=now - timedelta(days=1))
    for token in email_verification_tokens:
        user = token.user
        if not user.is_verified:
            user.delete()
        token.delete()
    PasswordChangeToken.objects.filter(created_at__lt=now - timedelta(hours=1)).delete()
