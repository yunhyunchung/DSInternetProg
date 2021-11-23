from django.db import models
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from markdownx.utils import markdown
import os

# Create your models here.
# 데이터베이스 생성, 데베에 모델 변화 내용 알리기(반영): python manage.py makemigrations => migrate

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)
    # slug: 사람이 읽을 수 있는 텍스트로 고유 URL 만들기 (한글도 허용)

    def __str__(self):  #카테고리 이름 반환
        return self.name

    def get_absolute_url(self):  # 카테고리 url (slug 이용)
        return f'/blog/tag/{self.slug}/'

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)
    # slug: 사람이 읽을 수 있는 텍스트로 고유 URL 만들기 (한글도 허용)

    def __str__(self):  #카테고리 이름 반환
        return self.name

    def get_absolute_url(self):  # 카테고리 url (slug 이용)
        return f'/blog/category/{self.slug}/'

    # Meta로 모델의 복수형(-s) 알려주기
    class Meta:
        verbose_name_plural = 'Categories'

class Post(models.Model):
    title = models.CharField(max_length=30)
    hook_text = models.CharField(max_length=100, blank=True)
    content = MarkdownxField()

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d', blank=True)
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)  # 처음 생성 시각
    updated_at = models.DateTimeField(auto_now=True)  # 수정 시각

    # 작성자 - 여러 개의 post 모델과 1명의 user 연결 (다대일 관계)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    # Post 모델에 category 필드 추가(Category 모델과 연결)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    # 다대다 관계: Post 모델에 tag 필드 추가(Tag 모델과 연결)
    tags = models.ManyToManyField(Tag, blank=True)

    #Post 제목
    def __str__(self):
        return f'[{self.pk}]{self.title} :: {self.author}'

    #각각의 Post url
    def get_absolute_url(self):
        return f'/blog/{self.pk}/'

    # 첨부파일명, 확장자
    def get_file_name(self):
        return os.path.basename(self.file_upload.name)

    def get_file_ext(self):
        return self.get_file_name().split('.')[-1]

    # content에 마크다운 문법 적용해서 html로 만든다
    def get_content_markdown(self):
        return markdown(self.content)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author}::{self.content}'

    def get_absolute_url(self):
        return f'{self.post.get_absolute_url()}#comment-{ self.pk }'

    def get_avatar_url(self):
        if self.author.socialaccount_set.exists():
            return self.author.socialaccount_set.first().get_avatar_url()
        else:
            return 'https://doitdjango.com/avatar/id/406/e497d9096d10c45c/svg/{self.author.email}'