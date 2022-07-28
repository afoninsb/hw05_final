from django.test import TestCase
from django.urls import reverse

from posts.models import User
from yatube.utils import InitMixin


class FormTest(InitMixin, TestCase):

    def test_signup_form(self):
        """При отправке валидной формы reverse(users:signup)
        создаётся новый пользователь."""
        self.assertEqual(User.objects.count(), 2)
        url = reverse('users:signup')
        password = self.fake.word().capitalize() + self.fake.isbn10()
        data_post = {
            'first_name': self.fake.first_name(),
            'last_name': self.fake.last_name(),
            'username': self.fake.user_name(),
            'email': self.fake.ascii_safe_email(),
            'password1': password,
            'password2': password,
        }
        redirect = reverse('posts:index')
        response = self.unauth_client.post(
            url, data=data_post)
        self.assertEqual(User.objects.count(), 3)
        last_user = User.objects.last()
        self.assertEqual(last_user.first_name, data_post['first_name'])
        self.assertEqual(last_user.last_name, data_post['last_name'])
        self.assertEqual(last_user.username, data_post['username'])
        self.assertEqual(last_user.email, data_post['email'])
        self.assertRedirects(response, redirect)
