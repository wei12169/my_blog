from django.contrib.auth.models import User
from django.http.response import HttpResponse
from django.shortcuts import redirect, render

from comment.models import Comment

from .forms import ArticlePostForm
from .models import ArticlePost
import markdown
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
#引入Q对象
from django.db.models import Q

# Create your views here.
def article_list(request):
    search = request.GET.get('search')
    order = request.GET.get('order')
    if search:
        #根据GET请求中查询条件返回不同排序的对象数组
        if order == 'total_views':
            article_list = ArticlePost.objects.filter(
                Q(title__icontains=search) |
                Q(body__icontains=search)
            ).order_by('-total_views')
        else:
            article_list = ArticlePost.objects.filter(
                Q(title__icontains=search) |
                Q(body__icontains=search)
            )
    else:
        search = ''
        if order == 'total_views':
            article_list = ArticlePost.objects.all().order_by('-total_views')
        else:
            article_list = ArticlePost.objects.all()
    #每页显示文章数
    paginator = Paginator(article_list, 3)
    #获取url中的页码
    page = request.GET.get('page')
    #将导航对象相应的页码内容返回给articles
    articles = paginator.get_page(page)
    #需要传递给模板的对象
    context = {'articles': articles, 'order': order, 'search': search}
    #render函数，载入模板，并返回context对象
    return render(request, 'article/list.html', context)

# 文章详情
def article_detail(request, id):
    #取出相应的文章
    article = ArticlePost.objects.get(id=id)
    #取出文章评论
    comments = Comment.objects.filter(article=id)

    #浏览量 +1
    article.total_views += 1
    article.save(update_fields=['total_views'])

    #将markdown语法渲染成html样式
    md = markdown.Markdown(
        extensions=[
            #包含 缩写，表格等常用拓展
            'markdown.extensions.extra',
            #语法高亮拓展
            'markdown.extensions.codehilite',
            #目录拓展
            'markdown.extensions.toc',
        ]
    )
    article.body = md.convert(article.body)
    #需要传递给模板的对象
    context = {'article': article, 'toc': md.toc, 'comments': comments}
    #载入模板，并返回context对象
    return render(request, 'article/detail.html', context)

#写文章的视图
@login_required(login_url='/userprofile/login/')
def article_create(request):
    #判断用户是否提交数据
    if request.method == 'POST':
        #将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(data=request.POST)
        #判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            #保存数据，但暂时不提交到数据库中
            new_article = article_post_form.save(commit=False)
            #指定数据库中id=1的用户为作者
            new_article.author = User.objects.get(id=request.user.id)
            #将新文章保存到数据库中
            new_article.save()
            #完成后返回文章列表
            return redirect('article:article_list')
        #如果数据不合法，返回错误信息
        else:
            return HttpResponse('表单内容有误，请重新填写。')
    #如果用户请求获取数据
    else:
        #创建表单类实例
        article_post_form = ArticlePostForm()
        #赋值上下文
        context = {'article_post_form': article_post_form}
        #返回模板
        return render(request, 'article/create.html', context)

#删除文章
def article_delete(request, id):
    #根据id获取需要删除的文章
    article = ArticlePost.objects.get(id=id)
    #调用.delect()方法删除文章
    article.delete()
    #完成后返回文章列表
    return redirect('article:article_list')

#安全删除文章
@login_required(login_url='/userprofile/login/')
def article_safe_delete(request, id):
    article = ArticlePost.objects.get(id=id)
    if request.user != article.author:
            return HttpResponse('你没有权限删除此用户信息。')
    if request.method == 'POST':
        article = ArticlePost.objects.get(id=id)
        article.delete()
        return redirect('article:article_list')
    else:
        return HttpResponse('仅允许post请求')

#更新文章
@login_required(login_url='/userprofile/login/')
def article_update(request, id):
    """
    更新文章的视图函数
    通过POST方法提交表单，更新title、body字段
    GET方法进入初始表单页面
    id: 文章的 id
    """

    # 获取需要修改的具体文章对象
    article = ArticlePost.objects.get(id=id)
    if request.user != article.author:
            return HttpResponse('你没有权限编辑此用户文章。')
    # 判断用户是否为 POST 提交表单数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(data=request.POST)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存新写入的 title、body 数据并保存
            article.title = request.POST['title']
            article.body = request.POST['body']
            article.save()
            # 完成后返回到修改后的文章中。需传入文章的 id 值
            return redirect("article:article_detail", id=id)
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    # 如果用户 GET 请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm()
        # 赋值上下文，将 article 文章对象也传递进去，以便提取旧的内容
        context = {'article': article, 'article_post_form': article_post_form}
        # 将响应返回到模板中
        return render(request, 'article/update.html', context)