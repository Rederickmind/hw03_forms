from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


def get_page_obj(queryset, request):
    """Создание Paginator с нужным queryset"""
    # Количество постов на странице
    POSTS_AMOUNT = 10
    # Показывать по POSTS_AMOUNT записей на странице.
    paginator = Paginator(queryset, POSTS_AMOUNT)
    # Из URL извлекаем номер запрошенной страницы
    page_number = request.GET.get('page')
    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)
    return {
        'page_obj': page_obj
    }
    

def index(request):
    """Главная страница"""
    context = get_page_obj(Post.objects.all(), request)
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Получение постов нужной группы по запросу"""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    context = {
        'group': group,
    }
    context.update(get_page_obj(posts, request))
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Отображение профиля пользователя"""
    # Код запроса к модели User
    user = get_object_or_404(User, username=username)
    post_list = user.posts.all()
    post_quantity = user.posts.count()
    context = {
        'username': user,
        'post_quantity': post_quantity
    }
    context.update(get_page_obj(post_list, request))
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Функция для просмотра поста"""
    # Код запроса к модели Posts
    post = get_object_or_404(Post, id=post_id)
    context = {
        'post': post
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Функция создания нового поста"""
    form = PostForm(request.POST or None)
    user = request.user
    context = {
        'form': form
    }
    if not form.is_valid():
        return render(request, 'posts/post_create.html', context)
    new_post = form.save(commit=False)
    new_post.author = request.user
    new_post.save()
    return redirect('posts:profile', user.username)


@login_required
def post_edit(request, post_id):
    """Функция для редактирования поста"""
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST, instance=post)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': PostForm(instance=post),
        'post': post,
        'is_edit': True
    }
    return render(request, 'posts/post_create.html', context)
