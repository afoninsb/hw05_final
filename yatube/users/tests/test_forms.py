from django.test import TestCase
from django.urls import reverse
from faker import Faker

from posts.models import User


class FormTest(TestCase):

    def test_signup_form(self):
        """При отправке валидной формы users:signup
        создаётся новый пользователь."""
        count_start = User.objects.count()
        url = reverse('users:signup')
        fake = Faker()
        password = fake.word().capitalize() + fake.isbn10()
        data_post = {
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'username': fake.user_name(),
            'email': fake.ascii_safe_email(),
            'password1': password,
            'password2': password,
        }
        redirect = reverse('posts:index')
        response = self.client.post(url, data=data_post)
        count_end = User.objects.count()
        self.assertEqual(count_end - count_start, 1)
        last_user = User.objects.last()
        self.assertEqual(last_user.first_name, data_post['first_name'])
        self.assertEqual(last_user.last_name, data_post['last_name'])
        self.assertEqual(last_user.username, data_post['username'])
        self.assertEqual(last_user.email, data_post['email'])
        self.assertRedirects(response, redirect)
