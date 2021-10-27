from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Post

# CBV
class PostList(ListView):
    model = Post
    ordering = '-pk'
#   template_name = 'blog/post_list.html'
# post_list.html - 기본 템플릿

class PostDetail(DetailView):
    model = Post
# post_detail.html - 기본 템플릿

# FBV
#def index(request):
#    posts = Post.objects.all().order_by('-pk')  // 데이터베이스에 쿼리(명령어) 날리기
#    return render(request, 'blog/post_list.html',
#                  {
#                      'posts': posts  // posts를 딕셔너리 형태로 html에 전달
#                  }
#                  )
#def single_post_page(request, pk):
#    post = Post.objects.get(pk=pk)
#    return render(request, 'blog/post_detail.html',
#                  {
#                      'post': post
#                  }
#                  )