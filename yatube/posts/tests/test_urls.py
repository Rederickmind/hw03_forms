# posts/tests/test_urls.py
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus
from ..models import Group, Post
from django.urls import reverse

User = get_user_model()


class PostsURLTests(TestCase):
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
        self.author_client.force_login(PostsURLTests.post.author)

    # Тестирование общедоступных страниц
    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_page(self):
        response = self.guest_client.get('/group/test_group/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_page(self):
        response = self.guest_client.get(
            f'/profile/{PostsURLTests.user.username}/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_page(self):
        response = self.guest_client.get(f'/posts/{self.post.pk}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # Проверка ошибки при переходе на несуществующую страницу
    def test_unexisting_page_error(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    # Проверка редиректа неавторизованного пользователя
    def test_unauthorized_redirect_create_page(self):
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response,
            reverse('users:login') + '?next=' + reverse('posts:post_create'),
        )

    # Проверка страницы доступной авторизованному пользователю
    def test_create_page(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # Проверка страницы редактирования поста автором и не автором
    def test_edit_post_by_author(self):
        response = self.author_client.get(
            f'/posts/{PostsURLTests.post.pk}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post_by_not_author(self):
        response = self.authorized_client.get(
            f'/posts/{PostsURLTests.post.pk}/edit/', follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostsURLTests.post.pk}
            ),
        )

    # Проверка шаблонов неавторизованного пользователя
    def test_unauthorized_templates_use(self):
        public_urls = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{PostsURLTests.group.slug}/',
            'posts/profile.html': f'/profile/{PostsURLTests.user.username}/',
            'posts/post_detail.html': f'/posts/{PostsURLTests.post.pk}/',
        }
        for template, url in public_urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    # Проверка шаблонов авторизованного пользователя
    def test_authorized_templates_use(self):
        logged_in_urls = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{PostsURLTests.group.slug}/',
            'posts/profile.html': f'/profile/{PostsURLTests.user.username}/',
            'posts/post_detail.html': f'/posts/{PostsURLTests.post.pk}/',
            'posts/post_create.html': '/create/'
        }

        for template, url in logged_in_urls.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    # Проверка шаблона для автора поста
    def test_post_author_template_use(self):
        response = self.author_client.get(
            f'/posts/{PostsURLTests.post.pk}/edit/'
        )
        self.assertTemplateUsed(response, 'posts/post_create.html')
