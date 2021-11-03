from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Post, Category, Tag

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

def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    # post와 tag는 다대다 관계 => 여러 개 tag들을 가져옴
    # (카테고리는 다대일 관계 => post가 속하는 하나의 카테고리만 가져옴)
    post_list = tag.post_set.all() # Post.objects.filter(tags=tag) 아님

    return render(request, 'blog/post_list.html',
                  {
                      'post_list': post_list,
                      'tag': tag,
                      'categories': Category.objects.all(),
                      'no_category_post_count': Post.objects.filter(category=None).count(),
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