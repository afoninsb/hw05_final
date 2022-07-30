from http import HTTPStatus

from django.test import TestCase


class ErrorsTest(TestCase):

    def test_404_template(self):
        """Cтраница 404 отдает кастомный шаблон."""
        template = 'core/404.html'
        response = self.client.get('/page_not_found/')
        self.assertTemplateUsed(response, template)
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
