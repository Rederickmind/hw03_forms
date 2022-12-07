from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User
from .forms import PostForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required


def index(request):
    """Главная страница"""
    posts = Post.objects.all()
    # Показывать по 10 записей на странице.
    paginator = Paginator(posts, 10)

    # Из URL извлекаем номер запрошенной страницы
    page_number = request.GET.get('page')

    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }

    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Получение постов нужной группы по запросу"""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    # Показывать по 10 записей на странице.
    paginator = Paginator(posts, 10)

    # Из URL извлекаем номер запрошенной страницы
    page_number = request.GET.get('page')

    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


# Функция для профиля пользователя
def profile(request, username):
    # Код запроса к модели User
    user = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=user)
    post_quantity = post_list.count()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'username': user,
        'page_obj': page_obj,
        'post_quantity': post_quantity
    }
    return render(request, 'posts/profile.html', context)


# Функция для просмотра поста
def post_detail(request, post_id):
    # Код запроса к модели Posts
    post = get_object_or_404(Post, id=post_id)
    context = {
        'post': post
    }
    return render(request, 'posts/post_detail.html', context)


# Функция создания нового поста
@login_required
def post_create(request):
    form = PostForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            form.cleaned_data['text']
            form.cleaned_data['group']
            post.author = request.user
            post.save()
            return redirect('posts:profile', post.author.username)
    context = {
        'form': form
    }
    return render(request, 'posts/post_create.html', context)


# Функция для редактирования поста
@login_required
def post_edit(request, post_id):
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
