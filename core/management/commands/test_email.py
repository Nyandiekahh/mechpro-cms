"""
Send a real test email to verify the Gmail app-password setup.

    python manage.py test_email you@example.com

Uses whatever EMAIL_BACKEND the current settings resolve to — so in
development it prints to the terminal unless SEND_REAL_EMAILS=True.
"""
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Send a test email to the given address."

    def add_arguments(self, parser):
        parser.add_argument("to", help="Recipient email address")

    def handle(self, *args, **options):
        backend = settings.EMAIL_BACKEND
        self.stdout.write(f"Backend: {backend}")
        self.stdout.write(f"From:    {settings.DEFAULT_FROM_EMAIL}")
        self.stdout.write(f"Host:    {settings.EMAIL_HOST}:{settings.EMAIL_PORT} "
                          f"(user {settings.EMAIL_HOST_USER})")
        if "console" in backend:
            self.stdout.write(self.style.WARNING(
                "Console backend active — this will PRINT below, not send. "
                "Set SEND_REAL_EMAILS=True in .env to send for real."))
        send_mail(
            subject="MECHPRO website — email test",
            message=("This is a test from the MECHPRO backend. If you are "
                     "reading this in an inbox, SMTP and the Gmail app "
                     "password are working."),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[options["to"]],
            fail_silently=False,
        )
        self.stdout.write(self.style.SUCCESS("send_mail() completed without errors."))
