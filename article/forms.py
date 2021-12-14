from django import forms
from django.db import models
from django.forms import fields
from .models import ArticlePost

class ArticlePostForm(forms.ModelForm):
    class Meta:
        #指明数据模型来源
        model = ArticlePost
        #定义表单包含的字段
        fields = ('title', 'body','column', 'tags')
