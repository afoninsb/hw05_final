from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from posts.models import Comment, Post
from yatube.utils import InitMixin


class FormTest(InitMixin, TestCase):

    def test_create_post(self):
        """Валидная форма создает запись в Post.
        Производится редирект в профиль автора."""
        self.assertEqual(Post.objects.count(), 1)
        url = reverse('posts:post_create')
        data_post = {
            'text': self.fake.sentence(nb_words=10),
            'group': self.group.id,
        }
        redirect = reverse(
            'posts:profile', kwargs={'username': self.author.username})
        response = self.author_post.post(
            url, data=data_post)
        self.assertEqual(Post.objects.count(), 2)
        first_post = Post.objects.first()
        self.assertEqual(first_post.text, data_post['text'])
        self.assertEqual(first_post.group.id, data_post['group'])
        self.assertEqual(first_post.author, self.author)
        self.assertRedirects(response, redirect)

    def test_edit_post(self):
        """Валидная форма обновляет запись в Post.
        Производится редирект на страницу поста"""
        first_post = Post.objects.first()
        url = reverse(
            'posts:post_edit', kwargs={'post_id': first_post.id})
        data_post = {
            'text': self.fake.sentence(nb_words=10),
            'group': self.group_two.id,
        }
        redirect = reverse(
            'posts:post_detail', kwargs={'post_id': first_post.id})
        response = self.author_post.post(
            url, data=data_post)
        self.assertEqual(Post.objects.count(), 1)
        first_post.refresh_from_db()
        self.assertEqual(first_post.text, data_post['text'])
        self.assertEqual(first_post.group.id, data_post['group'])
        self.assertEqual(first_post.author, self.author)
        self.assertRedirects(response, redirect)

    def test_create_edit_post(self):
        """Создаём и меняем пост. id и автор - остаются,
        текст и группа - меняются."""
        url = reverse('posts:post_create')
        data_post = {
            'text': self.fake.sentence(nb_words=10),
            'group': self.group.id,
        }
        self.author_post.post(url, data=data_post)
        post_create = Post.objects.first()
        self.assertEqual(post_create.text, data_post['text'])
        self.assertEqual(post_create.group.id, data_post['group'])
        url = reverse(
            'posts:post_edit', kwargs={'post_id': post_create.id})
        data_post = {
            'text': self.fake.sentence(nb_words=12),
            'group': self.group_two.id,
        }
        self.author_post.post(url, data=data_post)
        post_edit = Post.objects.order_by('-pub_date').first()
        self.assertEqual(post_edit.text, data_post['text'])
        self.assertEqual(post_edit.group.id, data_post['group'])
        self.assertEqual(post_edit.author, post_create.author)
        self.assertEqual(post_edit.id, post_create.id)

    def test_create_post_with_image(self):
        """При отправке поста с картинкой через форму PostForm
        создаётся запись в базе данных."""
        self.assertEqual(Post.objects.count(), 1)
        url = reverse('posts:post_create')
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        data_post = {
            'text': self.fake.sentence(nb_words=10),
            'group': self.group.id,
            'image': uploaded,
        }
        self.auth_client.post(url, data=data_post)
        self.assertEqual(Post.objects.count(), 2)

    def test_comments(self):
        """Комментарий от неавторизованного пользователя не попадает в базу.
        Комментарий от авторизованного пользователя сохраняется в базе."""
        count1 = Comment.objects.count()
        url = reverse('posts:add_comment', kwargs={'post_id': self.post.id})
        data_comment = {
            'text': self.fake.sentence(nb_words=10),
        }
        self.unauth_client.post(url, data=data_comment)
        count2 = Comment.objects.count()
        self.assertEqual(count1, count2)
        self.auth_client.post(url, data=data_comment)
        count3 = Comment.objects.count()
        self.assertEqual(count3 - count1, 1)

    def test_valid_comments(self):
        """После успешной отправки комментарий появляется на странице поста."""
        url = reverse('posts:add_comment', kwargs={'post_id': self.post.id})
        data_comment = {
            'text': self.fake.sentence(nb_words=10),
        }
        self.auth_client.post(url, data=data_comment)
        post = Post.objects.get(pk=self.post.id)
        comment = post.comments.first()
        url = reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        response = self.unauth_client.get(url)
        self.assertEqual(
            response.context.get('comments')[0], comment)
