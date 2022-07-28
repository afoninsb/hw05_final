from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from yatube.utils import InitMixin


class AboutTest(InitMixin, TestCase):

    def test_pages_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.unauth_client.get(reverse_name)
                self.assertEqual(HTTPStatus.OK, response.status_code)
                self.assertTemplateUsed(response, template)
