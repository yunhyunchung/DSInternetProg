from django.db import models
from django.contrib.auth.models import User
import os

# Create your models here.
# 데이터베이스 생성, 데베에 모델 변화 내용 알리기(반영): python manage.py makemigrations => migrate

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)
    # slug: 사람이 읽을 수 있는 텍스트로 고유 URL 만들기 (한글도 허용)

    def __str__(self):  #카테고리 이름 반환
        return self.name

    # Meta로 모델의 복수형(-s) 알려주기
    class Meta:
        verbose_name_plural = 'Categories'

class Post(models.Model):
    title = models.CharField(max_length=30)
    hook_text = models.CharField(max_length=100, blank=True)
    content = models.TextField()

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d', blank=True)
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)  # 처음 생성 시각
    updated_at = models.DateTimeField(auto_now=True)  # 수정 시각

    # 작성자 - 여러 개의 post 모델과 1명의 user 연결 (다대일 관계)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    # Post 모델에 category 필드 추가
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)

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