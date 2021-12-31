from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE
from django.utils import timezone
from django.urls.base import reverse
from taggit.managers import TaggableManager
from PIL import Image

# Create your models here.

class ArticleColumn(models.Model):
    title = models.CharField(max_length=100, blank=True)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.title

#博客文章数据类型
class ArticlePost(models.Model):
    def was_created_recently(self):
        diff = timezone.now() - self.created
        
        # if diff.days <= 0 and diff.seconds < 60:
        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
            return True
        else:
            return False
    #文章栏目的'一对多'外键
    column = models.ForeignKey(
        ArticleColumn,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='article',
    )

    #文章标题图
    avatar = models.ImageField(upload_to='article/%Y%m%d', blank=True)

    #保存时处理图片
    def save(self, *args, **kwargs):
        #调用原有的save()功能
        article = super(ArticlePost, self).save(*args, **kwargs)

        #固定宽度缩放图片大小
        if self.avatar and not kwargs.get('update_fields'):
            image = Image.open(self.avatar)
            (x, y) = image.size
            new_x = 400
            new_y = int(new_x * (y / x))
            resize_image = image.resize((new_x, new_y), Image.ANTIALIAS)
            resize_image.save(self.avatar.path)
        
        return article

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

    #文章标签
    tags = TaggableManager(blank=True)

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