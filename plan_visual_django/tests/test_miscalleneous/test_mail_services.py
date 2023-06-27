from unittest import skip

from django.core.mail import send_mail
from django.test import TestCase
from django.conf import settings


class TestMailServices(TestCase):
    @skip
    def test_send_smtp_email(self):
        """
        Tests normal Python email sending outside of Django - helps in initial debugging of email sending.
        :return:
        """
        import smtplib, ssl, os

        port = os.environ.get("EMAIL_PORT")
        password = os.environ.get("EMAIL_PASSWORD")
        username = os.environ.get("EMAIL_USERNAME")

        # Create a secure SSL context
        context = ssl.create_default_context()

        SUBJECT = "Message from python"

        TEXT = """\
        This message is sent from Python."""

        message = f'Subject: {SUBJECT}\n\n{TEXT}'

        with smtplib.SMTP_SSL("mail.genonline.co.uk", port, context=context) as server:
            server.login("thomas.gaylard@genonline.co.uk", password)
            server.sendmail("thomas.gaylard@genonline.co.uk", ["testing@genonline.co.uk"], message)

    @skip
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