from django.db import models
import os

# Create your models here.
# 데이터베이스 생성, 데베에 모델 변화 내용 알리기(반영): python manage.py makemigrations => migrate

class Post(models.Model):
    title = models.CharField(max_length=30)
    hook_text = models.CharField(max_length=100, blank=True)
    content = models.TextField()

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d', blank=True)
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)  # 처음 생성 시각
    updated_at = models.DateTimeField(auto_now=True)  # 수정 시각

    #author: 추후 작성 예정

    #Post 제목
    def __str__(self):
        return f'[{self.pk}]{self.title}'

    #각각의 Post url
    def get_absolute_url(self):
        return f'/blog/{self.pk}/'

    # 첨부파일명, 확장자
    def get_file_name(self):
        return os.path.basename(self.file_upload.name)

    def get_file_ext(self):
        return self.get_file_name().split('.')[-1]