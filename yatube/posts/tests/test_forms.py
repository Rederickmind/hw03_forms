from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Group, Post, User
from django.urls import reverse
from posts.forms import PostForm

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )

        cls.form = PostForm()

    def setUp(self):
        # Создаем авторизованый клиент
        self.user = User.objects.create_user(username='Nikita_Test')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        '''
        При отправке валидной формы создаётся пост
        и происходит редирект на Профиль
        '''
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост'
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост'
            ).exists()
        )

    def test_post_edit(self):
        '''
        Проверка что валидная форма изменяет пост отобранный по id
        и происходит редирект на post_detail
        '''
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост для изменения'
        )

        posts_count = Post.objects.count()
        post_id = self.post.id

        form_data = {
            'text': 'Изменённый тестовый пост'
        }

        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                args=({post_id})
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                args=({self.post.id})
            )
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFalse(
            Post.objects.filter(
                text='Тестовый пост для изменения'
            ).exists())
        self.assertTrue(
            Post.objects.filter(
                text='Изменённый тестовый пост'
            ).exists())
