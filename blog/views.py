from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Post, Category

# CBV
class PostList(ListView):
    model = Post
    ordering = '-pk'

    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context

#   template_name = 'blog/post_list.html'
# post_list.html - 기본 템플릿

class PostDetail(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context

# 해당 카테고리 안의 post들을 보여주는 페이지
def category_page(request, slug):
    if slug == 'no_category':
        category = '미분류'
        post_list = Post.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)
        post_list = Post.objects.filter(category=category)
    return render(request, 'blog/post_list.html',
                  {
                      'post_list': post_list,
                      'categories': Category.objects.all(),
                      'no_category_post_count': Post.objects.filter(category=None).count(),
                      'category': category,
                  }
                  )


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