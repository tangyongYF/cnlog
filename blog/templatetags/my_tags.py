from django.db.models import Count

from blog.models import *

from django import template

# register = template.library()


# @register.inclusion_tag("classification.html")
def get_classification_style(username):
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
