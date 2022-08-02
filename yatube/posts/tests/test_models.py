from django.conf import settings
from django.test import TestCase

from core.mixins import InitMixin


class ModelTest(InitMixin, TestCase):

    def test_str_group(self):
        """Проверяем __str__ моделей."""
        data = {
            self.group: self.group.title,
            self.post: self.post.text[:settings.SHORT_TEXT]
        }
        for model_name, model_str in data.items():
            with self.subTest(self):
                self.assertEqual(model_str, str(model_name))

    def test_verbose_name_help_text(self):
        """Проверяем verbose_name и help_text модели Post."""
        data = {
            self.post._meta.get_field('text').help_text: 'Введите текст поста',
            self.post._meta.get_field('group').help_text: 'Выберите группу',
            self.post._meta.get_field('text').verbose_name: 'Текст поста',
            self.post._meta.get_field('pub_date').verbose_name:
                'Дата создания',
            self.post._meta.get_field('author').verbose_name: 'Автор',
            self.post._meta.get_field('group').verbose_name: 'Группа'
        }
        for key, value in data.items():
            with self.subTest(self):
                self.assertEqual(key, value)
