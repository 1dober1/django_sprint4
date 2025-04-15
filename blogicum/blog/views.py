from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.contrib.auth.views import LoginView
from django.urls import reverse

from .models import Post, Category, User


def filter_published_posts(queryset):
    return queryset.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    )


def index(request):
    template = 'blog/index.html'
    posts = filter_published_posts(
        Post.objects.select_related('category', 'author', 'location')
    )[:5]
    context = {'post_list': posts}
    return render(request, template, context)


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

    context = {
        'category': category,
        'post_list': posts
    }

    return render(request, template_name, context)


def profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user_profile)
    context = {
        'profile': user_profile,
        'page_obj': posts
    }
    return render(request, 'blog/profile.html', context)


class CustomLoginView(LoginView):
    def get_success_url(self):
        username = self.request.user.username  # type: ignore
        return reverse('blog:profile', kwargs={'username': username})
