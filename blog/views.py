from django.db.models import Count, Prefetch
from django.shortcuts import render, get_object_or_404

from blog.models import Comment, Post, Tag


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title if post.tags.exists() else '',
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_with_tag,
    }


def index(request):
    prefetch_tags = Tag.objects.prefetch_with_posts_count()

    most_popular_posts = (
        Post.objects.popular()
        .prefetch_related('author', prefetch_tags)[:5]
        .fetch_with_comments_count()
    )

    fresh_posts = (
        Post.objects.annotate(comments_count=Count('comments'))
        .order_by('-published_at')
        .select_related('author')
        .prefetch_related(prefetch_tags)
    )
    most_fresh_posts = fresh_posts[:5]

    most_popular_tags = Tag.objects.with_posts_count().popular()[:5]

    context = {
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
        'page_posts': [
            serialize_post(post) for post in most_fresh_posts
        ],
        'popular_tags': [
            serialize_tag(tag) for tag in most_popular_tags
        ],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    prefetch_tags = Tag.objects.prefetch_with_posts_count()

    post = get_object_or_404(
        Post.objects
        .select_related('author')
        .prefetch_related(prefetch_tags, 'likes', 'comments__author')
        .annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments')
        ),
        slug=slug
    )

    serialized_comments = [
        {'text': comment.text, 'published_at': comment.published_at,
            'author': comment.author.username}
        for comment in post.comments.all()
    ]

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': post.likes_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.first().title if post.tags.exists() else '',
    }

    most_popular_tags = Tag.objects.with_posts_count().popular()[:5]

    most_popular_posts = (
        Post.objects.popular()
        .prefetch_related('author', prefetch_tags)[:5]
        .fetch_with_comments_count()
    )

    context = {
        'post': serialized_post,
        'popular_tags': [
            serialize_tag(tag) for tag in most_popular_tags
        ],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    prefetch_tags = Tag.objects.prefetch_with_posts_count()

    tag = get_object_or_404(
        Tag.objects.with_posts_count().prefetch_related('posts'), title=tag_title
    )

    most_popular_tags = Tag.objects.with_posts_count().popular()[:5]

    most_popular_posts = (
        Post.objects.popular()
        .prefetch_related('author', prefetch_tags)[:5]
        .fetch_with_comments_count()
    )

    related_posts = (
        Post.objects
        .filter(tags=tag)
        .annotate(comments_count=Count('comments'))
        .select_related('author')
        .prefetch_related(prefetch_tags)[:20]
    )

    context = {
        'tag': tag.title,
        'popular_tags': [
            serialize_tag(tag) for tag in most_popular_tags
        ],
        'posts': [
            serialize_post(post) for post in related_posts
        ],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
