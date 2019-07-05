from unittest.mock import patch

from django.test import TestCase
from django.core import mail
from django.urls import reverse
from django.contrib import auth
from main import forms

class TestForm(TestCase):
    def test_valid_contact_us_form_sends_email(self):
        form = forms.ContactForm({
            'name': "Luke Skywalker",
            'message': "Hi there"})

        self.assertTrue(form.is_valid())

        with self.assertLogs('main.forms', level='INFO') as cm: form.send_mail()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Site message')

        self.assertGreaterEqual(len(cm.output), 1)

    def test_invalid_contact_us_form(self):
        form = forms.ContactForm({
            'message': "Hi there"})
        self.assertFalse(form.is_valid())

    def test_valid_contact_us_form_works(self):
        response = self.client.get(reverse("contact_us"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/contact_form.html')
        self.assertContains(response, 'BookTime')
        self.assertIsInstance(
            response.context["form"], forms.ContactForm
        )

    def test_valid_signup_form_sends_email(self):
        form = forms.UserCreationForm(
            {
                "email": "user@domain.com",
                "password1": "abcabcabc",
                "password2": "abcabcabc",
            }
        )
        self.assertTrue(form.is_valid())

        with self.assertLogs("main.forms", level="INFO") as cm:
            form.send_mail()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject, "Welcome to BookTime"
            )
        self.assertGreaterEqual(len(cm.output), 1)

class TestPage(TestCase):
    def test_user_signup_page_loads_correctly(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "signup.html")
        self.assertContains(Response, "BookTime")
        self.assertIsInstance(
            response.context["form"],
            forms.UserCreationForm
            )
    def test_user_signup_page_submission_works(self):
        post_data = {
            "email": "user@domain.com",
            "password1": "abcabcabc",
            "password2": "abcabcabc",
        }
        with patch.object(
            forms.UserCreationForm, "send_mail"
            ) as mock_send:
                response = self.client.post(
                    reverse("signup"), post_data
                )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            models.User.objects.filter(
                email="user@domain.com"
            ).exists()
        )
        self.assertTrue(
            auth.get_user(self.client).is_authenticated
        )
        mock_send.assert_called_once()
