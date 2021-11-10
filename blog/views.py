from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post, Category, Tag
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify

# CBV
class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):  # UserPasses~와 CreateView 순서대로...
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']

    # 이 클래스에 접근 가능한 사용자 설정
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    # 작성한 폼 처리
    def form_valid(self, form):
        current_user = self.request.user
        # 로그인 & 스태프 또는 슈퍼유저(관리자)
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
            form.instance.author = current_user   # 로그인한 사용자를 작성자로 자동 입력
            response = super(PostCreate, self).form_valid(form)  # 새로 생성한 포스트 페이지 저장
            # input에 입력한 tag들 처리 (tag를 구분자로 분리 & 새로 생성한 tag의 slug 생성 & 새 포스트에 입력한 tag 연결)
            tags_str = self.request.POST.get('tags_str')
            if tags_str:
                tags_str = tags_str.strip()

                tags_str = tags_str.replace(',', ';')
                tags_list = tags_str.split(';')

                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)

            return response
        else:
            return redirect('/blog/')

class PostUpdate(LoginRequiredMixin, UpdateView):  # 모델명_form.html: 기본 템플릿
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']

    template_name = 'blog/post_update_form.html'

    # GET 방식의 요청인지 POST 방식의 요청인지 확인하는 함수
    def dispatch(self, request, *args, **kwargs):
        # 로그인한 방문자가 특정 포스트의 작성자가 맞는지 확인
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied  # 403 오류 - 접근 권한 없음

    # template(html)로 추가 인자 넘기기 - 여기선 기존의 태그를 이은 문자열 'tags_str_default'
    def get_context_data(self, **kwargs):
        context = super(PostUpdate, self).get_context_data()
        if self.object.tags.exists():
            tags_str_list = list()
            for t in self.object.tags.all():
                tags_str_list.append(t.name)
            context['tags_str_default'] = '; '.join(tags_str_list)
        return context

    # 폼이 유효하면 받은 tags 값 처리
    def form_valid(self, form):
        response = super(PostUpdate, self).form_valid(form)  # 새로 생성한 포스트 페이지 저장
        self.object.tags.clear()  # 수정 페이지에서는 이미 존재하는 tags 제거 -> 새로 들어온 tags로 채움

        # input에 입력한 tag들 처리 (tag를 구분자로 분리 & 새로 생성한 tag의 slug 생성 & 새 포스트에 입력한 tag 연결)
        tags_str = self.request.POST.get('tags_str')
        if tags_str:
            tags_str = tags_str.strip()

            tags_str = tags_str.replace(',', ';')
            tags_list = tags_str.split(';')

            for t in tags_list:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(name=t)
                if is_tag_created:
                    tag.slug = slugify(t, allow_unicode=True)
                    tag.save()
                self.object.tags.add(tag)

        return response


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