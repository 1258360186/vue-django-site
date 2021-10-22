from django.urls import path
from blog import api
from blog import payapi

urlpatterns = [
    path('add-article/',api.add_article),
    path('delete-article/',api.delete_article),
    path('article-list/',api.article_list),
    path('baiyu-checkperm/',api.user_permisson),
    path('baiyu-newgroup/',api.baiyu_newgroup),
    path('baiyu-userlist/',api.baiyu_userlist),
    path('baiyu-lanmu/',api.baiyu_lanmu),
    path('baiyu-article/',api.baiyu_article),
    path('baiyu-userarticle/',api.baiyu_userarticle),
    path('baiyu-articlelike/',api.baiyu_articlelike),
    path('baiyu-articlefavor/',api.baiyu_articlefavor),
    path('baiyu-pinglun/',api.baiyu_pinglun),
    path('baiyu-login/',api.baiyu_login),
    path('baiyu-register/',api.baiyu_register),
    path('auto-login/',api.auto_login),
    path('baiyu-logout/',api.baiyu_logout),
    path('get-alipay-url/',payapi.getALipayurl)
]