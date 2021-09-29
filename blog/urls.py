from django.urls import path
from . import views

urlpatterns = [
    path('<int:pk>/', views.single_post_page),
    path('', views.index),  # 서버IP/blog
]