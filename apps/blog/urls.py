from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('blog/', views.post_list, name='post_list'),
    path('blog/category/<slug:slug>/', views.category_post_list, name='category_post_list'),
    path('blog/<slug:slug>/', views.post_detail, name='post_detail'),
]
