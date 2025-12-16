# (c) ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, 2021-2025.

from django.core import mail
from django.core.mail.message import EmailMessage
from django.template.loader import render_to_string
from django.test import TestCase


class TestsEpflMailTemplates(TestCase):
    def test_send_epflmail_for_actu(self):

        html = render_to_string("actu.html")
        email = EmailMessage(
            "Email Actu", html, "from@example.com", ["to@example.com"]
        )
        email.send()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Email Actu")
        self.assertInHTML("<p>This is Actu.</p>", mail.outbox[0].body)
        self.assertIn("logo.png", mail.outbox[0].body)
        self.assertIn("EPFL, all rights reserved", mail.outbox[0].body)
        self.assertNotIn("square.png", mail.outbox[0].body)
        self.assertNotIn("Online version", mail.outbox[0].body)

    def test_send_epflmail_for_memento(self):

        html = render_to_string("memento.html", {"APP_TITLE": "Memento"})
        email = EmailMessage(
            "Email Memento", html, "from@example.com", ["to@example.com"]
        )
        email.send()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Email Memento")
        self.assertInHTML("<p>This is Memento.</p>", mail.outbox[0].body)
        self.assertIn("logo.png", mail.outbox[0].body)
        self.assertIn("EPFL, all rights reserved", mail.outbox[0].body)
        self.assertIn("square.png", mail.outbox[0].body)
        self.assertIn("Online version", mail.outbox[0].body)
