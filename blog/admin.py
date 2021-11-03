from django.contrib import admin
from .models import Post, Category

# 관리자 페이지에 Post, Category 모델 등록하기
admin.site.register(Post)

# Category 모델의 name 필드를 이용해 자동으로 slug 만든다.
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}

admin.site.register(Category, CategoryAdmin)
