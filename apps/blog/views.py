from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Post, BlogCategory

def post_list(request):
    queryset = Post.live.filter(status='published').select_related('category', 'author').order_by('-published_at')
    
    paginator = Paginator(queryset, 12)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    context = {
        'posts': posts,
        'categories': BlogCategory.objects.all(),
        'popular_posts': Post.live.filter(status='published').order_by('-views_count')[:4]
    }
    return render(request, 'blog/list.html', context)

def category_post_list(request, slug):
    category = get_object_or_404(BlogCategory, slug=slug)
    queryset = Post.live.filter(status='published', category=category).select_related('author').order_by('-published_at')
    
    paginator = Paginator(queryset, 12)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'posts': posts,
        'categories': BlogCategory.objects.all(),
    }
    return render(request, 'blog/list.html', context)

def post_detail(request, slug):
    post = get_object_or_404(Post.live.all(), slug=slug, status='published')
    
    # Update views count
    post.views_count += 1
    post.save(update_fields=['views_count'])
    
    related_posts = Post.live.filter(
        status='published',
        category=post.category
    ).exclude(id=post.id).order_by('-published_at')[:3]
    
    context = {
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'blog/detail.html', context)
