from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from .forms import UserLoginForm, UserRegisterForm
from django.contrib.auth.models import User
#引入验证登录的装饰器
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from .models import Profile

# Create your views here.

def user_login(request):
    if request.method == 'POST':
        user_login_form = UserLoginForm(data=request.POST)
        if user_login_form.is_valid():
            # .cleaned_data 清洗出合法数据
            data = user_login_form.cleaned_data
            #校验账号，密码是否正确匹配数据库中的某个账户
            #如果匹配则返回这个user对象
            user = authenticate(username=data['username'], password=data['password'])
            if user:
                #将用户数据保存在session中，即实现了登录动作
                login(request, user)
                return redirect('article:article_list')
            else:
                return HttpResponse('账号或者密码输入错误')
        else:
            return HttpResponse('账号或者密码输入不合法')
    elif request.method == 'GET':
        user_login_form = UserLoginForm()
        context = {'form': user_login_form}
        return render(request, 'userprofile/login.html', context)
    else:
        return HttpResponse('请使用GET或POST请求数据')

#用户退出
def user_logout(request):
    logout(request)
    return redirect('article:article_list')

#用户注册
def user_register(request):
    if request.method == 'POST':
        user_register_form = UserRegisterForm(data=request.POST)
        if user_register_form.is_valid():
            new_user = user_register_form.save(commit=False)
            #设置密码
            new_user.set_password(user_register_form.cleaned_data['password'])
            new_user.save()
            #保存好数据立即登录并返回博客列表首页
            login(request, new_user)
            return redirect('article:article_list')
        else:
            return HttpResponse('注册输入有误，请重试。')
    elif request.method == 'GET':
        user_register_form = UserRegisterForm()
        context = {'form': user_register_form}
        return render(request, 'userprofile/register.html', context)
    else:
        return HttpResponse('请使用GET或者POST请求数据')

#用户删除
@login_required(login_url='/userprofile/login/')
def user_delete(request, id):
    if request.method == 'POST':
        user = User.objects.get(id=id)
        #验证登录用户、带删除用户是否相同
        if request.user == user:
            #退出登录，删除数据并返回博客列表
            logout(request)
            user.delete()
            return redirect('article:article_list')
        else:
            return HttpResponse('你没有权限删除。')
    else:
        return HttpResponse('仅接受post请求。')

#编辑用户信息
@login_required(login_url='/userprofile/login/')
def profile_edit(request, id):
    user = User.objects.get(id=id)
    #user_id是OneToOneField自动生成的字段
    #旧代码
    # profile = Profile.objects.get(user_id=id)
    #修改后的代码
    if Profile.objects.filter(user_id=id).exists():
        profile = Profile.objects.get(user_id=id)
    else:
        profile = Profile.objects.create(user=user)

    if request.method == 'POST':
        #验证修改数据者，是否为用户本人
        if request.user != user:
            return HttpResponse('你没有权限修改此用户信息。')

        profile_form = ProfileForm(data=request.POST)
        if profile_form.is_valid():
            #取得清洗后的合法数据
            profile_cd = profile_form.cleaned_data
            profile.phone = profile_cd['phone']
            profile.bio = profile_cd['bio']
            profile.save()
            #带参数的redirect()
            return redirect('userprofile:edit', id=id)
        else:
            return HttpResponse('注册表单输入有误，请重试。')

    elif request.method == 'GET':
        profile_form = ProfileForm()
        context = {'profile_form':profile_form, 'profile':profile, 'user':user}
        return render(request, 'userprofile/edit.html', context)
    else:
        return HttpResponse('请使用GET或POST请求数据')
