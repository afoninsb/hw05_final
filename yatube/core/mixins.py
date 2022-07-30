import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
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
        cls.group = Group.objects.create(
            title=cls.fake.sentence(nb_words=5),
            slug=('_').join(cls.fake.words(nb=5)),
            description=cls.fake.sentence(nb_words=15)
        )
        cls.post = Post.objects.create(
            text=cls.fake.sentence(nb_words=10),
            author=cls.author,
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.author_post = Client()
        self.author_post.force_login(self.author)
        self.auth_client = Client()
        self.auth_client.force_login(self.auth_user)
        cache.clear()
