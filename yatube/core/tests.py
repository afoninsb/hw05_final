from django.test import TestCase

from yatube.utils import InitMixin


class ErrorsTest(InitMixin, TestCase):

    def test_404_template(self):
        """Cтраница 404 отдает кастомный шаблон."""
        template = 'core/404.html'
        response = self.auth_client.get('/page_not_found/')
        self.assertTemplateUsed(response, template)
