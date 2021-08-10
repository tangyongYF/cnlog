from django.db.models import Count, F
from django.shortcuts import render, HttpResponse, redirect
# Create your views here.
from django.http import JsonResponse
from django.contrib import auth
from blog.my_forms import *
from blog.models import *
import json
from django.http import JsonResponse
from django.db import transaction
from django.core.mail import send_mail
import threading
from   cnblog import settings

def login(request):
    response = {"user": None, "msg": None}
    if request.method == "POST":
        user = request.POST.get("user")
        pwd = request.POST.get("pwd")
        valid_code = request.POST.get("vid")
        random_str = request.session.get("random_str")
        if not valid_code.upper() == random_str.upper():
            print("验证码错误！！！")
            response["msg"] = "valid is wrong!!!"
        else:
            print("验证码正确！！")
            user = auth.authenticate(username=user, password=pwd)
            if user:
                auth.login(request, user)
                response["user"] = user.username
                print(f"request.user.username:{request.user.username}")
                print(f"request.user.pwd:{request.user.password}")
            else:
                response["msg"] = "user or password is wrong!!!"
                print("user or password is wrong!!!")
        return JsonResponse(response)

    return render(request, "login.html")


def get_validCode_img(request):
    # 方式二
    # def get_color():
    #     import random
    #     return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    #
    # img = Image.new("RGB", (270, 40), color=get_color())
    #
    # with open("ValidCode.png", "wb") as f:
    #     img.save(f, "png")
    #
    # with open("ValidCode.png", "rb") as f:
    #     data = f.read()
    #
    # return HttpResponse(data)

    # 方式三
    # def get_color():
    #     import random
    #     return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    #
    # img = Image.new("RGB", (270, 40), color=get_color())
    #
    # from io import BytesIO
    #
    # f = BytesIO()
    # img.save(f, "png")
    # data = f.getvalue()

    # 方式四
    from blog.util.valid_code_img import get_valid_code_imgss

    data = get_valid_code_imgss(request)

    return HttpResponse(data)


def index(request):
    article_obj = Article.objects.all()

    return render(request, "index.html", {"article_obj": article_obj})


def register(request):
    if request.is_ajax():
        form = forms_user(request.POST)
        response = {"user": None, "msg": None}
        if form.is_valid():
            print(f"clean_data:{form.cleaned_data}")
            response["user"] = form.cleaned_data.get("user")
            user = form.cleaned_data.get("user")
            pwd = form.cleaned_data.get("pwd")
            email = form.cleaned_data.get("email")
            avatar = request.FILES.get("via")
            print(f"user:{user}")
            if avatar:
                user_obj = UserInfo.objects.create_user(username=user, password=pwd, email=email, avatar=avatar)
            else:
                user_obj = UserInfo.objects.create_user(username=user, password=pwd, email=email)
        else:
            print(f"clean_data:{form.cleaned_data}")
            print(f"errors:{form.errors}")
            response["msg"] = form.errors
        return JsonResponse(response)

    form = forms_user()

    return render(request, "register.html", locals())


def login_out(request):
    auth.logout(request)

    return redirect("/login/")


def get_querydata(username):
    user = UserInfo.objects.filter(username=username).first()
    blog = user.blog
    Category_num = Category.objects.values("pk").annotate(c=Count("article__title")).values("title", "c")

    # 查询当前站点的每一个分类名称以及对应的文章数
    blog_category_num = Category.objects.filter(blog=blog).annotate(c=Count("article__title")).values("title", "c")

    # 查询当前站点的每一个标签名称以及对应的文章数
    tag_title_num = Tag.objects.filter(blog=blog).values("pk").annotate(c=Count("article__title")).values_list("title",
                                                                                                               "c")

    # 查询当前站点每一个年月的名称以及对应的文章数
    # # 方式一
    date_title_num = Article.objects.filter(user=user).extra(
        select={"Y_m_d_modle": "date_format(create_time,'%%Y-%%m-%%d')"}).values(
        "Y_m_d_modle").annotate(
        c=Count("title")).values_list("Y_m_d_modle", "c")
    return {"user": user, "blog": blog, "Category_num": Category_num, "blog_category_num": blog_category_num,
            "tag_title_num": tag_title_num, "date_title_num": date_title_num}


def home_site(request, username, **kwargs):
    user = get_querydata(username).get("user")

    if not user:
        return render(request, "not_found.html")
    if kwargs:
        condition = kwargs.get("condition")
        parm = kwargs.get("parm")
        if condition == "category":
            article_list = Article.objects.filter(user=user).filter(category__title=parm)
        elif condition == "tag":
            article_list = Article.objects.filter(user=user).filter(tags__title=parm)
        else:
            year, month, day = parm.split("-")
            article_list = Article.objects.filter(user=user).filter(create_time__year=year, create_time__month=month,
                                                                    create_time__day=day)
    else:
        # 当前用户或者当前站点对应所有文章

        article_list = Article.objects.filter(user=user)

    # 查询每一个分类名称以及对应的文章数
    # res=article_list.values("tags").annotate(Count("title")).values("tags__title")
    # print(f"title_num{res}")
    # 方式二
    # from django.db.models.functions import TruncMonth
    #
    # date_title_num = Article.objects.filter(user=user).annotate(month=TruncMonth("create_time")).values(
    #     "month").annotate(
    #     c=Count("nid")).values_list("title", "month", "c")
    # print(f"查询当前站点每一个年月的名称以及对应的文章数{date_title_num}")
    content = get_querydata(username)
    content['username'] = username
    content['article_list'] = article_list

    return render(request, "home_site.html",
                  content)


def article_deatile(request, username, article_id):
    content_sum = get_querydata(username)
    content_sum['username'] = username
    article_obj = Article.objects.filter(pk=article_id).first()
    content_sum["article_obj"] = article_obj
    comment_obj = Comment.objects.filter(article_id=article_id)
    content_sum["comment_obj"]=comment_obj
    print(f"comment_obj:{comment_obj}")
    return render(request, "article_deatile.html", content_sum)


def diggt(request):
    print(f"request.POST{request.POST}")
    is_up = json.loads(request.POST.get("is_up"))
    article_id = request.POST.get("article_id")
    print(f"is_up{type(is_up)},article_id:{article_id}")
    user_id = request.user.pk
    print(f"user:{user_id},user_type:{type(user_id)}")
    response = {"state": True, "handle": None}
    res = ArticleUpDown.objects.filter(article_id=article_id, user_id=user_id).first()
    if not res:
        ArticleUpDown.objects.create(article_id=article_id, is_up=is_up, user_id=user_id)
        if is_up:
            Article.objects.filter(pk=article_id).update(up_count=F("up_count") + 1)
        else:
            Article.objects.filter(pk=article_id).update(down_count=F("down_count") + 1)
    else:
        response["state"] = False
    response["handle"] = is_up

    return HttpResponse(json.dumps(response))


def content(request):
    response={}
    print(request.POST)
    content = request.POST.get("content")
    article_id = request.POST.get("article_id")
    user_id = request.user.pk
    pid = request.POST.get("pid")
    article_obj=Article.objects.filter(pk=article_id).first()

    with transaction.atomic():
        comment_obj=Comment.objects.create(content=content, user_id=user_id, article_id=article_id, parent_comment_id=pid)
        create_time=comment_obj.create_time.strftime("%Y-%m-%d %H:%X")
        Article.objects.filter(pk=article_id).update(comment_count=F("comment_count")+1)

    # 发送邮件
    article_title=article_obj.title
    # send_mail(f"你的文章{article_title}收到一条评论内容",content,settings.EMAIL_HOST_USER,["tangyongr@qq.com"])
    t=threading.Thread(target=send_mail,args=(f"你的文章{article_title}收到一条评论内容",content,settings.EMAIL_HOST_USER,["tangyongr@qq.com"]))
    t = threading.Thread(target=send_mail, args=("您的文章%s新增了一条评论内容" % article_title,
                                                 content,
                                                 settings.EMAIL_HOST_USER,
                                                 ["tangyongr@qq.com"])
                         )
    t.start()

    username=request.user.username
    response["create_time"]=create_time
    response["content"]=content
    response["username"]=username

    if pid:
        print(f"pid:{pid}")
        parent_pk = comment_obj.parent_comment.pk
        print(f"parent_pk{parent_pk}")
        parent_content = comment_obj.parent_comment.content
        response["parent_pk"]=parent_pk
        response["parent_content"]=parent_content
        response["parent_name"]=comment_obj.parent_comment.user.username
    response = json.dumps(response)

    return HttpResponse(response)

def get_conment_tree(request):
    article_id=request.GET.get("article_id")
    res=Comment.objects.filter(article_id=article_id).order_by("pk").values("content","nid","parent_comment_id")
    print(res)
    res=json.dumps(list(res))

    return HttpResponse(res)
