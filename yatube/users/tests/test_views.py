from http import HTTPStatus

from django import forms
from django.test import TestCase
from django.urls import reverse

from yatube.utils import InitMixin


class ViewsTest(InitMixin, TestCase):

    def test_pages_uses_correct_template_auth(self):
        """URL-адрес использует соответствующий шаблон
        для авторизованного пользователя."""
        templates_pages_names = {
            reverse('users:password_change_done'):
                'users/password_change_done.html',
            reverse('users:password_change_form'):
                'users/password_change_form.html',
            reverse('users:logout'): 'users/logged_out.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.auth_client.get(reverse_name)
                self.assertEqual(HTTPStatus.OK, response.status_code)
                self.assertTemplateUsed(response, template)

    def test_pages_uses_correct_template_unauth(self):
        """URL-адрес использует соответствующий шаблон
        для неавторизованного пользователя"""
        templates_pages_names = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:password_reset_done'):
                'users/password_reset_done.html',
            reverse('users:password_reset_form'):
                'users/password_reset_form.html',
            reverse('users:password_reset_confirm',
                    kwargs={'uidb64': self.fake.pystr(max_chars=2),
                            'token': self.fake.pystr(max_chars=20)}):
                'users/password_reset_confirm.html',
            reverse('users:password_reset_complete'):
                'users/password_reset_complete.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.unauth_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
                self.assertEqual(HTTPStatus.OK, response.status_code)

    def test_signup_context(self):
        """Шаблон 'users:signup' сформирован с правильным контекстом.
        Проверяем правильность полей формы."""
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
            'password1': forms.fields.CharField,
            'password2': forms.fields.CharField,
        }
        response = self.unauth_client.get(reverse('users:signup'))
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get(
                    'form').fields.get(value)
                self.assertIsInstance(form_field, expected)
