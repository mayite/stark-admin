# 注册功能
from app01 import models
from stark.service.stark import site, ModelStark
from django.utils.safestring import mark_safe

class BookConfig(ModelStark):
    list_display = ['title', 'price','publish']


site.register(models.Book, BookConfig)

site.register(models.Publish)
site.register(models.Author)
site.register(models.AuthorDetail)
