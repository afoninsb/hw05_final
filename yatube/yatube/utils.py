import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from faker import Faker

from posts.models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class InitMixin:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.auth_user = User.objects.create_user(username='user')
        cls.fake = Faker()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title=cls.fake.sentence(nb_words=5),
            slug=('_').join(cls.fake.words(nb=5)),
            description=cls.fake.sentence(nb_words=15)
        )
        cls.post = Post.objects.create(
            text=cls.fake.sentence(nb_words=10),
            author=cls.author,
            group=cls.group,
            image=cls.uploaded
        )
        cls.group_two = Group.objects.create(
            title=cls.fake.sentence(nb_words=6),
            slug=('_').join(cls.fake.words(nb=3)),
            description=cls.fake.sentence(nb_words=13)
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.author_post = Client()
        self.author_post.force_login(self.author)
        self.auth_client = Client()
        self.auth_client.force_login(self.auth_user)
        self.unauth_client = Client()
        cache.clear()
