from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from yatube.utils import InitMixin


class URLTest(InitMixin, TestCase):

    def test_accessibility(self):
        """Страницы, доступные любому пользователю."""
        addresses = [
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': self.author.username}),
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        ]
        for address in addresses:
            with self.subTest(address=address):
                response = self.unauth_client.get(address)
                self.assertEqual(HTTPStatus.OK, response.status_code)

    def test_url_authorized_client_template(self):
        """Корректность шаблонов «публичных» страниц
        при посещении неавторизованным пользователем."""
        url_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.author.username}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
                'posts/post_detail.html',
        }
        for address, template in url_templates.items():
            with self.subTest(address=address):
                response = self.auth_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_url_author_post_template(self):
        """Корректность шаблонов «приватных» страниц при посещении автором."""
        url_templates = {
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
                'posts/create_post.html',
        }
        for address, template in url_templates.items():
            with self.subTest(address=address):
                response = self.author_post.get(address)
                self.assertTemplateUsed(response, template)

    def test_not_accessibility(self):
        """Страницы, недоступные неавторизованному пользователю.
        При попытке доступа производится редирект на страницу авторизации."""
        addresses = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        ]
        for address in addresses:
            with self.subTest(address=address):
                response = self.client.get(address)
                url = reverse('users:login')
                self.assertRedirects(
                    response, f'{url}?next={address}')

    def test_not_accessibility_authorized(self):
        """Авторизованный пользователь, не являющийся автором поста,
        при переходе на страницу редактирования поста, перенаправляется
        на страницу своего профиля."""
        response = self.auth_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}))
        self.assertRedirects(response, (reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id})))

    def test_accessibility_authorized(self):
        """Страницы, доступные авторизованному пользователю и автору."""
        responses = [
            self.auth_client.get(reverse('posts:post_create')),
            self.author_post.get(reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}))
        ]
        for response in responses:
            with self.subTest(response=response):
                self.assertEqual(HTTPStatus.OK, response.status_code)
