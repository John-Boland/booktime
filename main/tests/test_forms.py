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

    def test_add_to_basket_loggedin_works(self):
        user1 = models.User.objects.create_user(
            "user1@a.com", "pw432joij"
        )
        cb = models.Product.objects.create(
            name="The cathedral and the bazaar"
            slug="cathedra-bazaar",
            price=Decimal("10.00"),

        )
        w = models.Product.objects.create(
            name="Microsoft Windows guide",
            slug="microsoft-windows-guide",
            price=Decimal("12.00"),
        )
        self.client.force_login(user1)
        response = self.client.get(
            reverse("add_to_basket"), {"product_id": cb.id}
        )
        self.assertTrue(
            models.Basket.objects.filter(user=user1).exists()
        )
        self.assertEquals(
            models.BasketLine.objects.filter(
                basket__user=user1
            ).count(),
            1,
        )
        response = self.client.get(
            reverse("add_too_basket"), {"product_id": w.id}
        )
        self.assertEquals(
            models.BasketLine.objects.filter(
                basket__user=user1
            ).count(),
            2,
        )
