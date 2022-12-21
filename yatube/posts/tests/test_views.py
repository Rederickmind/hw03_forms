from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Group, Post
from django.urls import reverse

User = get_user_model()


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.user = User.objects.create_user(username='Nikita_Test')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Создаем клиент автора тестового поста
        self.author_client = Client()
        self.author_client.force_login(PostsViewsTests.post.author)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            'posts/index.html': reverse('posts:homepage'),
            'posts/group_list.html': reverse(
                'posts:group_posts',
                kwargs={'slug': 'test_group'}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': f'{PostsViewsTests.user.username}'}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{PostsViewsTests.post.pk}'}
            ),
            'posts/post_create.html': (
                reverse('posts:post_create')
            )
        }
        # Проверяем, что при обращении к name
        # вызывается соответствующий HTML-шаблон
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_edit_by_author_uses_correct_template(self):
        """
        Проверка шаблона редактирования поста автором posts/post_create.html
        """
        response = self.author_client.\
            get(reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{PostsViewsTests.post.pk}'}
            )
            )
        self.assertTemplateUsed(response, 'posts/post_create.html')

    # Проверка контекстов в view функциях
