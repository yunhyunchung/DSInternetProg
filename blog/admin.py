from django.contrib import admin
from .models import Post, Category, Tag

# 관리자 페이지에 Post, Category 모델 등록하기
admin.site.register(Post)

# Category 모델의 name 필드를 이용해 자동으로 slug 만든다.
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}
# Tag 모델의 name 필드를 이용해 자동으로 slug 만든다.
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}

#관리자 페이지에 Category, Tag, slug 정의한 클래스 등록하기
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
