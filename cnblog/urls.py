"""cnblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from blog import views
from django.views.static import serve
from  cnblog import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'login/', views.login),
    re_path(r'get_validCode_img/', views.get_validCode_img),
    re_path(r'index/$', views.index),
    re_path(r'register/', views.register),
    re_path(r'login_out/', views.login_out),
    # media配置
    re_path(r"media/(?P<path>.*)$",serve,{"document_root":settings.MEDIA_ROOT}),
    # 个人站点的路由配置
    re_path(r"index/(?P<username>\w+)/$",views.home_site),
    # 个人站点的url
    re_path(r"index/(?P<username>\w+)/(?P<condition>tag|category|archive)/(?P<parm>.*)/$",views.home_site),
    # 个人文章详情页
    re_path(r"index/(?P<username>\w+)/articles/(?P<article_id>\d+)/$",views.article_deatile),
    re_path(r"diggt/",views.diggt),
    re_path(r"content/",views.content),
    re_path(r"get_conment_tree/",views.get_conment_tree),
]
