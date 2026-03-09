import json

from django.test import TestCase

from .forms import ContactForm
from .models import VisitorLog


class ContactFormTests(TestCase):
    def test_rejects_short_message(self):
        form = ContactForm(
            data={
                "name": "Jean",
                "email": "jean@example.com",
                "subject": "Salut",
                "message": "court",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("message", form.errors)

    def test_accepts_valid_payload(self):
        form = ContactForm(
            data={
                "name": "Jean Dupont",
                "email": "jean@example.com",
                "subject": "Demande de devis",
                "message": "Bonjour, je souhaite discuter d'un projet web securise.",
            }
        )
        self.assertTrue(form.is_valid())


class ActivityLogTests(TestCase):
    def test_middleware_creates_visitor_log(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(VisitorLog.objects.count(), 1)
        log = VisitorLog.objects.first()
        self.assertEqual(log.path, "/")

    def test_time_spent_endpoint_updates_latest_log(self):
        self.client.get("/")
        response = self.client.post(
            "/activity/time-spent/",
            data=json.dumps({"path": "/", "time_spent_seconds": 12}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        log = VisitorLog.objects.order_by("-timestamp").first()
        self.assertEqual(log.time_spent_seconds, 12)
