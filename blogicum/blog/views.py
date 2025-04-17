from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.core.paginator import Paginator

from .forms import CustomUserChangeForm, AddPostForm
from .models import Category, Post, User


def filter_published_posts(queryset):
    return queryset.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    )


def index(request):
    posts = filter_published_posts(
        Post.objects.select_related('category', 'author', 'location')
    )

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(
        filter_published_posts(Post.objects.select_related(
            'category', 'author', 'location')),
        pk=post_id
    )
    template = 'blog/detail.html'
    context = {'post': post}
    return render(request, template, context)


def category_posts(request, category_slug):
    template_name = 'blog/category.html'

    category = get_object_or_404(
        Category.objects.filter(is_published=True),
        slug=category_slug
    )

    posts = filter_published_posts(
        category.posts.select_related(  # type: ignore
            'author', 'category', 'location')
    )

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'page_obj': page_obj
    }

    return render(request, template_name, context)


def profile(request, username):
    user_profile = get_object_or_404(User, username=username)

    if request.user == user_profile:
        posts = Post.objects.filter(author=user_profile).order_by('-pub_date')
    else:
        posts = Post.objects.filter(
            author=user_profile,
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile': user_profile,
        'page_obj': page_obj
    }
    return render(request, 'blog/profile.html', context)


class CustomLoginView(LoginView):
    def get_success_url(self):
        username = self.request.user.username  # type: ignore
        return reverse('blog:profile', kwargs={'username': username})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(reverse(
                'blog:profile',
                kwargs={'username': request.user.username}
            ))
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, 'blog/user.html', {'form': form})


@login_required
def create_post(request):
    form = AddPostForm(request.POST or None, files=request.FILES or None)
    context = {'form': form}
    if form.is_valid():
        post = form.save(commit=False, author=request.user)
        post.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', context)


@login_required
def edit_post(request, post_id=None):
    instance = get_object_or_404(Post, pk=post_id)

    if instance.author != request.user:
        return redirect('blog:post_detail', post_id=instance.pk)

    form = AddPostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=instance
    )

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=instance.pk)

    context = {'form': form}
    return render(request, 'blog/create.html', context)
