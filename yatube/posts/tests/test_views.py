from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Group, Post
from django.urls import reverse
from django.core.paginator import Page
from django import forms

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
            group=cls.group
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
                kwargs={'username': f'{self.user.username}'}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{self.post.pk}'}
            ),
            'posts/post_create.html': (
                reverse('posts:post_create')
            )
        }
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
                kwargs={'post_id': f'{self.post.pk}'}
            )
            )
        self.assertTemplateUsed(response, 'posts/post_create.html')

    # Проверка контекстов в view функциях
    def test_homepage_show_correct_context(self):
        '''Шаблон home сформирован с правильным контекстом.'''
        response = self.authorized_client.get(reverse('posts:homepage'))
        self.assertIsInstance(response.context['page_obj'], Page)
        first_object = response.context['page_obj'][0]
        posts_text_0 = first_object.text
        posts_pub_date_0 = first_object.pub_date
        posts_author_0 = first_object.author
        posts_group_0 = first_object.group

        self.assertEqual(posts_text_0, self.post.text)
        self.assertEqual(posts_pub_date_0, self.post.pub_date)
        self.assertEqual(posts_author_0, self.post.author)
        self.assertEqual(posts_group_0, self.post.group)

    def test_group_page_show_correct_context(self):
        '''Шаблон group сформирован с правильным контекстом.'''
        response = self.authorized_client.get(reverse(
            'posts:group_posts',
            kwargs={'slug': self.group.slug}
        )
        )

        self.assertIsInstance(response.context['page_obj'], Page)
        self.assertIsInstance(response.context['group'], Group)
        first_object = response.context['page_obj'][0]
        posts_text_0 = first_object.text
        posts_pub_date_0 = first_object.pub_date
        posts_author_0 = first_object.author
        posts_group_0 = first_object.group

        self.assertEqual(posts_text_0, self.post.text)
        self.assertEqual(posts_pub_date_0, self.post.pub_date)
        self.assertEqual(posts_author_0, self.post.author)
        self.assertEqual(posts_group_0, self.post.group)

    def test_profile_page_show_correct_context(self):
        '''Шаблон profile сформирован с правильным контекстом.'''
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.post.author.username}
        )
        )

        self.assertIsInstance(response.context['page_obj'], Page)
        self.assertIsInstance(response.context['username'], User)
        self.assertEqual(
            response.context['post_quantity'],
            len(list(Post.objects.filter(
                author_id=self.post.author.id
            ))))
        first_object = response.context['page_obj'][0]
        posts_text_0 = first_object.text
        posts_pub_date_0 = first_object.pub_date
        posts_author_0 = first_object.author
        posts_group_0 = first_object.group

        self.assertEqual(posts_text_0, self.post.text)
        self.assertEqual(posts_pub_date_0, self.post.pub_date)
        self.assertEqual(posts_author_0, self.post.author)
        self.assertEqual(posts_group_0, self.post.group)

    def test_post_detail_page_show_correct_context(self):
        '''Шаблон post_detail сформирован с правильным контекстом.'''
        response = self.guest_client.get(reverse(
            "posts:post_detail",
            kwargs={"post_id": self.post.id}
        )
        )
        self.assertIsInstance(response.context['post'], Post)
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get('post').author, self.post.author)
        self.assertEqual(response.context.get('post').group, self.post.group)

    def test_create_edit_show_correct_context(self):
        '''Шаблон create_edit сформирован с правильным контекстом.'''
        response = self.author_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.id}
        )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_create_show_correct_context(self):
        '''Шаблон create сформирован с правильным контекстом.'''
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)


class PostsPaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )
        for i in range(1, 14):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост {i}',
                group=cls.group
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
        self.author_client.force_login(PostsPaginatorViewsTest.post.author)

    def test_homepage_first_page_contains_ten_records(self):
        '''Проверка: количество постов на первой странице Главной равно 10.'''
        response = self.client.get(reverse('posts:homepage'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_homepage_second_page_contains_three_records(self):
        '''Проверка: количество постов на первой странице Главной равно 3.'''
        response = self.client.get(reverse('posts:homepage') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_page_first_page_contains_ten_records(self):
        '''Проверка: количество постов на первой странице Группы равно 10.'''
        response = self.client.get(reverse(
            'posts:group_posts',
            kwargs={'slug': self.group.slug}
        )
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_page_second_page_contains_three_records(self):
        '''Проверка: количество постов на первой странице Группы равно 3.'''
        response = self.client.get(reverse(
            'posts:group_posts',
            kwargs={'slug': self.group.slug}
        ) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_page_first_page_contains_ten_records(self):
        '''Проверка: количество постов на первой странице Группы равно 10.'''
        response = self.client.get(reverse(
            'posts:profile',
            kwargs={'username': self.post.author.username}
        )
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_page_second_page_contains_three_records(self):
        '''Проверка: количество постов на первой странице Группы равно 3.'''
        response = self.client.get(reverse(
            'posts:profile',
            kwargs={'username': self.post.author.username}
        ) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)


# Проверка создания поста на главной, в профиле и в группе
class PostAdditionalCheck(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_group2',
            description='Тестовое описание другой группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
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
        self.author_client.force_login(PostAdditionalCheck.post.author)

    def test_check_post_on_homepage(self):
        '''Созданный пост отображается на Главной странице'''
        response = self.authorized_client.get(reverse('posts:homepage'))

        first_object = response.context['page_obj'][0]
        posts_text_0 = first_object.text
        posts_pub_date_0 = first_object.pub_date
        posts_author_0 = first_object.author
        posts_group_0 = first_object.group

        self.assertEqual(posts_text_0, self.post.text)
        self.assertEqual(posts_pub_date_0, self.post.pub_date)
        self.assertEqual(posts_author_0, self.post.author)
        self.assertEqual(posts_group_0, self.post.group)

    def test_check_post_in_group(self):
        '''Созданный пост отображается на странице Тестовой группы'''
        response = self.authorized_client.get(reverse(
            'posts:group_posts',
            kwargs={'slug': self.group.slug}
        )
        )

        first_object = response.context['page_obj'][0]
        posts_group_0 = first_object.group

        self.assertEqual(posts_group_0, self.post.group)

    def test_check_post_not_in_incorrect_group(self):
        '''Созданный пост не в Тестовой группе 2'''
        response = self.authorized_client.get(reverse(
            'posts:group_posts',
            kwargs={'slug': self.group.slug}
        )
        )

        first_object = response.context['page_obj'][0]
        posts_group_0 = first_object.group

        self.assertNotEqual(posts_group_0, self.group2)

    def test_check_post_in_user_profile(self):
        '''Созданный пост отображается в профиле автора'''
        response = self.author_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.post.author.username}
        )
        )
        first_object = response.context['page_obj'][0]
        posts_text_0 = first_object.text
        posts_pub_date_0 = first_object.pub_date
        posts_author_0 = first_object.author
        posts_group_0 = first_object.group

        self.assertEqual(posts_text_0, self.post.text)
        self.assertEqual(posts_pub_date_0, self.post.pub_date)
        self.assertEqual(posts_author_0, self.post.author)
        self.assertEqual(posts_group_0, self.post.group)
