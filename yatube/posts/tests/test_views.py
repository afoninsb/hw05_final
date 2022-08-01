from http import HTTPStatus
from random import randint

from django import forms
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from core.mixins import InitMixin
from posts.models import Follow, Group, Post, User
from yatube.settings import POSTS_PER_PAGE


class ViewsTest(InitMixin, TestCase):

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.author.username}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
                'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_post.get(reverse_name)
                self.assertTemplateUsed(response, template)
                self.assertEqual(HTTPStatus.OK, response.status_code)

    def test_lists_posts_context(self):
        """Шаблоны 'posts:group_posts' и 'posts:index'
        сформированы с правильным контекстом."""
        reverse_list = [
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}),
        ]
        for reverse_item in reverse_list:
            with self.subTest(reverse_item=reverse_item):
                response = self.author_post.get(reverse_item)
                first_object = response.context['page_obj'][0]
                self.assertEqual(
                    first_object.text, self.post.text)
                self.assertEqual(first_object.author, self.author)
                self.assertEqual(first_object.group, self.group)
                self.assertEqual(first_object.pub_date, self.post.pub_date)

    def test_post_create_context(self):
        """Шаблоны 'posts:post_create' и 'posts:post_edit'
        сформированы с правильным контекстом. Проверяем правильность
        полей формы."""
        reverse_list = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
        ]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for reverse_item in reverse_list:
            with self.subTest(reverse_item=reverse_item):
                response = self.author_post.get(reverse_item)
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context.get(
                            'form').fields.get(value)
                        self.assertIsInstance(form_field, expected)

    def test_post_detail_context(self):
        """Шаблон 'posts:post_detail' сформирован с правильным контекстом."""
        response = (self.author_post.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})))
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get('post').author, self.author)
        self.assertEqual(response.context.get('post').group, self.group)

    def test_profile_context(self):
        """Шаблон 'posts:profile' сформирован с правильным контекстом."""
        response = (self.author_post.get(
            reverse('posts:profile',
                    kwargs={'username': self.author.username})))
        self.assertEqual(response.context['page_obj'][0].text, self.post.text)
        self.assertEqual(response.context.get('author'), self.author)

    def test_not_in_group_context(self):
        """Шаблон 'posts:group_posts' сформирован с правильным контекстом -
        без поста в неродной группе."""
        group_new = Group.objects.create(
            title=self.fake.sentence(nb_words=5),
            slug=('_').join(self.fake.words(nb=5)),
            description=self.fake.sentence(nb_words=15)
        )
        response = (self.author_post.get(
            reverse('posts:group_posts',
                    kwargs={'slug': group_new.slug})))
        self.assertFalse(response.context['page_obj'])
        self.assertEqual(response.context['page_obj'].paginator.count, 0)

    def test_paginator(self):
        """Проверяем Paginator, что на с сраницах со списками постов
        правильное количество постов."""
        add_post = randint(1, POSTS_PER_PAGE)
        objs = [
            Post(
                text=self.fake.sentence(nb_words=10),
                author=self.author,
                group=self.group
            )
            for _ in range(POSTS_PER_PAGE + add_post - 1)
        ]
        Post.objects.bulk_create(objs)
        reverse_list = {
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': self.author.username}),
        }
        for reverse_name in reverse_list:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                count = len(response.context.get('page_obj').object_list)
                self.assertEqual(count, POSTS_PER_PAGE)
                response = self.client.get(
                    reverse_name, data={'page': 2})
                count = len(response.context.get('page_obj').object_list)
                self.assertEqual(count, add_post)

    def test_post_with_img_context(self):
        """При выводе поста с картинкой изображение передаётся в context."""
        reverses = (
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': self.author.username}),
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        for reverse_name in reverses:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(
                    response.context.get('post').image, self.post.image)

    def test_follow(self):
        """"Авторизованный пользователь может подписываться
        на других пользователей."""
        count_start = Follow.objects.filter(
            user=self.auth_user, author=self.author).count()
        reverse_name = reverse('posts:profile_follow',
                               kwargs={'username': self.author.username})
        self.auth_client.get(reverse_name)
        count_end = Follow.objects.filter(
            user=self.auth_user, author=self.author).count()
        self.assertEqual(count_end - count_start, 1)

    def test_unfollow(self):
        """"Авторизованный пользователь может отписываться
        от других пользователей."""
        Follow.objects.create(author=self.author, user=self.auth_user)
        count_start = Follow.objects.filter(
            user=self.auth_user, author=self.author).count()
        reverse_name = reverse('posts:profile_unfollow',
                               kwargs={'username': self.author.username})
        self.auth_client.get(reverse_name)
        count_end = Follow.objects.filter(
            user=self.auth_user, author=self.author).count()
        self.assertEqual(count_end - count_start, -1)

    def test_following_post(self):
        """"Новая запись пользователя появляется в ленте тех,кто
        на него подписан."""
        following = Follow.objects.create(
            author=self.author, user=self.auth_user)
        response = self.auth_client.get(reverse('posts:follow_index'))
        self.assertEqual(response.context.get('post'), self.post)
        self.assertEqual(
            response.context.get('post').author, following.author)

    def test_unfollowing_post(self):
        """"Новая запись пользователя не появляется в ленте тех,
        кто не подписан."""
        author = User.objects.create_user(username='new_author')
        post = Post.objects.create(
            text=self.fake.sentence(nb_words=10),
            author=author,
        )
        response = self.auth_client.get(reverse('posts:follow_index'))
        self.assertNotEqual(response.context.get('post'), post)


class CacheTest(TestCase):

    def setUp(self):
        cache.clear()

    def test_cache(self):
        """"Кеширование главной страницы."""
        author = User.objects.create_user(username='author')
        post = Post.objects.create(
            text='abrakadabra',
            author=author,
        )
        content = str(self.client.get(reverse('posts:index')).content)
        self.assertIn(post.text, content)
        post.delete()
        content = str(self.client.get(reverse('posts:index')).content)
        self.assertIn(post.text, content)
        cache.clear()
        content = str(self.client.get(reverse('posts:index')).content)
        self.assertNotIn(post.text, content)
