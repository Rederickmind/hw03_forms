from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

SYMBOLS_AMOUNT = 15


class Group(models.Model):
    title = models.CharField('Название группы', max_length=200)
    slug = models.SlugField('Ссылка на группу', unique=True)
    description = models.TextField('Описание группы')

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self) -> str:
        # Выводим текст поста
        return self.text[:SYMBOLS_AMOUNT]
