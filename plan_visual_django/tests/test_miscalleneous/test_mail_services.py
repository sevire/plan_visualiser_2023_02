import os
import smtplib
import ssl
from django.core.mail import send_mail
from django.test import TestCase
from django.conf import settings


class TestMailServices(TestCase):
    def test_send_smtp_email(self):
        """
        Tests normal Python email sending outside of Django - helps in initial debugging of email sending.
        :return:
        """

        port = settings.EMAIL_PORT
        host = os.environ.get("EMAIL_HOST")
        password = os.environ.get("EMAIL_PASSWORD")
        username = os.environ.get("EMAIL_USERNAME")

        # Create a secure SSL context
        context = ssl.create_default_context()

        SUBJECT = "Message from python"

        TEXT = """\
        This message is sent from Python."""

        message = f'Subject: {SUBJECT}\n\n{TEXT}'

        with smtplib.SMTP_SSL(host=host, port=port, context=context) as server:
            server.login(user=username, password=password)
            server.sendmail("thomas.gaylard@genonline.co.uk", ["testing@genonline.co.uk"], message)

    def test_send_django_email(self):
        """
        Just testing basic email send capability within Django - mostly to check how it's configured.

        :return:
        """
        backend = settings.EMAIL_BACKEND

        mail = send_mail(
            subject='Test from Django',
            message='Here is the message.',
            from_email='thomas.gaylard@genonline.co.uk',
            recipient_list=['pv_test@genonline.co.uk'],
            fail_silently=False,
            connection=None,
            html_message=None
        )
        self.assertEqual(mail, 0)