from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import get_paginator


@login_required
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    context = {
        'form': form,
    }
    if not form.is_valid():
        return render(request=request,
                      template_name='posts/create_post.html',
                      context=context)
    post = form.save(commit=False)
    post.author = request.user
    form.save()
    return redirect('posts:profile',
                    username=request.user.username)


@login_required
def post_edit(request, post_id):
    cur_post = get_object_or_404(Post, id=post_id)
    if cur_post.author != request.user:
        return redirect('posts:post_detail',
                        post_id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=cur_post)
    if not form.is_valid():
        context = {
            'form': form,
            'is_edit': True,
        }
        return render(request=request,
                      template_name='posts/create_post.html',
                      context=context)
    form.save()
    return redirect('posts:post_detail',
                    post_id=post_id)


@cache_page(settings.CACHE_TIME, key_prefix='index_page')
def index(request):
    posts = Post.objects.select_related('author', 'group')
    page_obj = get_paginator(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author', 'group')
    page_obj = get_paginator(request, posts)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.select_related('author').filter(author=author)
    page_obj = get_paginator(request, posts)
    user = request.user
    following = (
        request.user.is_authenticated and not Follow.objects.filter(
            user=user, author=author).exists()
    )
    context = {
        'page_obj': page_obj,
        'author': author,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.select_related('author')
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        form.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    user = request.user
    posts = Post.objects.select_related('author').filter(
        author__following__user=user)
    page_obj = get_paginator(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    if user != author:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=user, author=author).delete()
    return redirect('posts:profile', username=username)
