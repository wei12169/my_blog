from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls.base import reverse

# Create your models here.
#博客文章数据类型
class ArticlePost(models.Model):
    #文章作者。参数on_delete用于指定数据删除方式
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    #文章标题。models.CharField为字符串字段，用于保存比较短的字符串
    title = models.CharField(max_length=100)

    #文章正文。保存大量文本使用TextField
    body = models.TextField()

    #文章创建时间。参数default=timezone.now指定在创建数据时默认写入当前时间
    created = models.DateTimeField(default=timezone.now)

    #文章更新时间。参数auto_now=True指定每次数据更新时自动写入当前时间
    updated = models.DateTimeField(auto_now=True)

    total_views = models.PositiveIntegerField(default=0)

    #内部类class Meta用于给model定义元数据
    class Meta:
        #ordering指定模型返回的数据的排列顺序
        # '-created'表明数据应以倒序排列
        ordering = ('-created',)

    #函数__str__定义当调用对象的str()方法时返回值内容
    def __str__(self) -> str:
        #将文章标题返回
        return self.title

    #获取文章地址
    def get_absolute_url(self):
        return reverse('article:article_detail', args=[self.id])