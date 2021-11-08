from django.urls import path
from . import views

urlpatterns = [ # 서버IP/blog/ 주소 뒤를 잇는 url 정의
    # FBV로 페이지 만들기
#   path('<int:pk>/', views.single_post_page),
#   path('', views.index),  # 서버IP/blog 라면 views.py의 index() 함수 실행

    path('update_post/<int:pk>/', views.PostUpdate.as_view()),
    path('create_post/', views.PostCreate.as_view()),
    path('tag/<str:slug>/', views.tag_page),
    path('category/<str:slug>/', views.category_page),
    path('<int:pk>/', views.PostDetail.as_view()),  # 서버IP/blog/1
    path('', views.PostList.as_view()),  # 서버IP/blog
]