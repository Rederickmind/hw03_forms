from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField('название группы', max_length=200)
    slug = models.SlugField('ссылка на группу', unique=True)
    description = models.TextField('описание группы')

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField('текст поста')
    pub_date = models.DateTimeField('дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор поста'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='группа'
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self) -> str:
        # Выводим текст поста
        return self.text
