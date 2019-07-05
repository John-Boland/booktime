from django.test import TestCase
from django.urls import reverse

from decimal import Decimal
from main import models

class TestPage(TestCase):
    def test_home_page_works(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")
        self.assertContains(response, "BookTime")

    def test_about_us_works(self):
        response = self.client.get(reverse("about_us"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "about_us.html")
        self.assertContains(response, "BookTime")

    def test_products_page_returns_active(self):
        models.Product.objects.create(
            name="The Prince",
            slug="the-prince",
            price=Decimal("1.00")
        )
        models.Product.objects.create(
            name="The Great Gatsby",
            slug="the-great-gatsby",
            price=Decimal("3.00"),
            active=False,
        )
        response = self.client.get(
            reverse("products", kwargs={"tag": "all"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "BookTime")

        product_list = models.Product.objects.active().order_by(
            "name"
        )
        self.assertEqual(
            list(response.context["object_list"]),
            list(product_list),
        )

    def test_products_page_filters_by_tags_and_active(self):
        cb = models.Product.objects.create(
            name="The Prince",
            slug="the-prince",
            price=Decimal("1.00"),
        )
        cb.tags.create(name="Philosophy", slug="philosophy")
        models.Product.objects.create(
            name="Beyond Good and Evil",
            slug="beyond-good-and-evil",
            price=Decimal("2.00"),
        )
        response = self.client.get(
            reverse("products", kwargs={"tag":"philosophy"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "BookTime")

        product_list = (
            models.Product.objects.active()
            .filter(tags__slug="philosophy")
            .order_by("name")
        )
        self.assertEqual(list(response.context["object_list"]),
        list(product_list),)

    def test_address_list_page_returns_only_owned(self):
        user1 = models.User.objects.create_user(
            "user1", "pw432joij"
        )
        user2 = models.User.objects.create_user(
            "user2", "pw432joij"
        )
        models.Address.objects.create(
            user=user1,
            name="john kimball",
            address1="flat 2",
            address2="12 Stralz avenue",
            city="London",
            country="uk",
        )
        models.Address.objects.create(
            user=user2,
            name="marc kimball",
            address1="123 Deacon road",
            address2="12 Stralz avenue",
            city="London",
            country="uk",
        )
        self.client.force_login(user2)
        response = self.client.get(reverse("address_list"))
        self.assertEqual(response.status_code, 200)

        address_list = models.Address.objects.filter(user=user2)
        self.assertEqual(
            list(response.context["object_list"]),
            list(address_list),
        )
    def test_address_create_stores_user(self):
        user1 = models.User.objects.create_user(
            "user1",
            "pw432joij"
        )
        models.Address.objects.create(
            name="john kercher",
            address1="1 av st",
            address2="",
            "zip_code": "MA12GS",
            city="Manchester",
            country="uk",
        )
        self.client.force_login(user1)
        self.client.post(
            reverse("address_create"), post_data
        )
        self.assertTrue(
            models.Address.objects.filter(user=user1).exists()
        )
