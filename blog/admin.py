from django.contrib import admin
from blog.models import Article
from blog.models import Userinfo,Lanmu
from blog.models import Article,Userinfo,Lanmu,Pinglun,PayOrder,Favourite,Like

# Register your models here.
admin.site.register(Article)
admin.site.register(Userinfo)
admin.site.register(Lanmu)
admin.site.register(Pinglun)
admin.site.register(PayOrder)
admin.site.register(Favourite)
admin.site.register(Like)