# 注册功能
from app01 import models
from stark.service.stark import site, ModelStark
from django.utils.safestring import mark_safe
from django import forms


# Book类
class BookModelForm(forms.ModelForm):
    class Meta:
        model = models.Book
        fields = "__all__"
        error_messages = {
            "title": {"required": " 该字段不能为空"}
        }


# Book配置类
class BookConfig(ModelStark):
    list_display = ['title', 'price', 'publish']
    list_display_links = ['title']

    model_form_class = BookModelForm
    search_fields = ['title', 'price']

    # 批量删除
    def patch_delete(self,request,queryset):
        queryset.delete()
    patch_delete.desc = '批量删除'

    # 批量初始化
    def patch_init(self,request,queryset):
        queryset.update(price=0)
    patch_init.desc = '批量初始化'

    actions = [patch_delete,patch_init]

    list_filter = ['publish', 'authors']




site.register(models.Book, BookConfig)
site.register(models.Publish)
site.register(models.Author)
site.register(models.AuthorDetail)
