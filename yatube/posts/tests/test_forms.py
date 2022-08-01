from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from core.mixins import InitMixin
from posts.models import Comment, Group, Post


class FormTest(InitMixin, TestCase):

    def test_create_post(self):
        """Валидная форма создает запись в Post.
        Производится редирект в профиль автора."""
        count_start = Post.objects.count()
        url = reverse('posts:post_create')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        data_post = {
            'text': self.fake.sentence(nb_words=10),
            'group': self.group.id,
            'image': uploaded,
        }
        redirect = reverse(
            'posts:profile', kwargs={'username': self.author.username})
        response = self.author_post.post(
            url, data=data_post)
        count_end = Post.objects.count()
        self.assertEqual(count_end - count_start, 1)
        first_post = Post.objects.first()
        self.assertEqual(first_post.text, data_post['text'])
        self.assertEqual(first_post.group, self.group)
        self.assertEqual(first_post.author, self.author)
        self.assertIsNotNone(first_post.image)
        self.assertRedirects(response, redirect)

    def test_edit_post(self):
        """Валидная форма обновляет запись в Post.
        Производится редирект на страницу поста"""
        post_test = Post.objects.create(
            text=self.fake.sentence(nb_words=10),
            author=self.author,
            group=self.group,
        )
        count_start = Post.objects.count()
        group_new = Group.objects.create(
            title=self.fake.sentence(nb_words=5),
            slug='_'.join(self.fake.words(nb=5)),
            description=self.fake.sentence(nb_words=15)
        )
        url = reverse(
            'posts:post_edit', kwargs={'post_id': post_test.id})
        data_post = {
            'text': self.fake.sentence(nb_words=10),
            'group': group_new.id,
        }
        redirect = reverse(
            'posts:post_detail', kwargs={'post_id': post_test.id})
        response = self.author_post.post(url, data=data_post)
        count_end = Post.objects.count()
        self.assertEqual(count_start, count_end)
        post_test.refresh_from_db()
        self.assertEqual(post_test.text, data_post['text'])
        self.assertEqual(post_test.group, group_new)
        self.assertEqual(post_test.author, self.author)
        self.assertRedirects(response, redirect)

    def test_unauth_comments(self):
        """Комментарий от неавторизованного пользователя не попадает в базу."""
        count_start = Comment.objects.count()
        url = reverse('posts:add_comment', kwargs={'post_id': self.post.id})
        redirect = reverse('users:login')
        redirect_url = f"{redirect}?next={url}"
        data_comment = {
            'text': self.fake.sentence(nb_words=10),
        }
        response = self.client.post(url, data=data_comment)
        count_end = Comment.objects.count()
        self.assertEqual(count_start, count_end)
        self.assertRedirects(response, redirect_url)

    def test_auth_comments(self):
        """Комментарий от авторизованного пользователя сохраняется в базе."""
        count_start = Comment.objects.count()
        url = reverse('posts:add_comment', kwargs={'post_id': self.post.id})
        data_comment = {
            'text': self.fake.sentence(nb_words=10),
        }
        self.auth_client.post(url, data=data_comment)
        count_end = Comment.objects.count()
        self.assertEqual(count_end - count_start, 1)

    def test_valid_comments(self):
        """После успешной отправки комментарий появляется на странице поста."""
        url = reverse('posts:add_comment', kwargs={'post_id': self.post.id})
        data_comment = {
            'text': self.fake.sentence(nb_words=10),
        }
        self.auth_client.post(url, data=data_comment)
        comment = self.post.comments.first()
        url = reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        response = self.client.get(url)
        self.assertEqual(
            response.context.get('comments')[0], comment)

    def test_not_image(self):
        """Если в качестве image в форму передать файл, не являющийся
        изображением, то происходит ошибка формы."""
        count_start = Post.objects.count()
        url = reverse('posts:post_create')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.txt',
            content=small_gif,
            content_type='text/plain'
        )
        data_post = {
            'text': self.fake.sentence(nb_words=10),
            'image': uploaded,
        }
        self.author_post.post(url, data=data_post)
        count_end = Post.objects.count()
        self.assertEqual(count_end, count_start)
