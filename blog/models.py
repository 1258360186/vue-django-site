from django.db import models
from django.contrib.auth.models import User

# Create your models here.

#用户信息
class Userinfo(models.Model):
    
    headImg = models.CharField(null=True,blank=True,max_length=300)
    nickName = models.CharField(null=True,blank=True,max_length=20)
    belong = models.OneToOneField(User,on_delete=models.CASCADE,null=True,blank=True)
    
    def __int__(self):
        return self.id
    
#文章分类
class Lanmu(models.Model):
    
    name = models.CharField(null=True,blank=True,max_length=20)
    belong = models.ForeignKey("self",on_delete=models.SET_NULL,null=True,blank=True,related_name='lanmu_child')
    
    def __str__(self):
        return self.name

#博客文章
class Article(models.Model):
    
    title = models.CharField(null=True,blank=True,max_length=80)
    cover = models.CharField(null=True,blank=True,max_length=300)
    describe = models.CharField(null=True,blank=True,max_length=200)
    content = models.TextField()
    belong = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True,related_name='article_user')
    belong_lanmu = models.ForeignKey(Lanmu,on_delete=models.SET_NULL,null=True,blank=True,related_name='article_lanmu')
    
    def __int__(self):
        return self.id
    
#评论
class Pinglun(models.Model):
    
    belong_user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True,related_name='pinglun_user')
    belong_art = models.ForeignKey(Article,on_delete=models.CASCADE,null=True,blank=True,related_name='pinglun_article')
    text = models.CharField(null=True,blank=True,max_length=300)
    
    def __int__(self):
        return self.id    

#收藏
class Favourite(models.Model):
    
    belong_user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True,related_name='favour_user')
    belong_art = models.ForeignKey(Article,on_delete=models.CASCADE,null=True,blank=True,related_name='favour_article')
    
    def __int__(self):
        return self.id

#点赞
class Like(models.Model):
    
    belong_user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True,related_name='like_user')
    belong_art = models.ForeignKey(Article,on_delete=models.CASCADE,null=True,blank=True,related_name='like_article')
    
    def __int__(self):
        return self.id
    
#打赏
class PayOrder(models.Model):
    
    order = models.CharField(null=True,blank=True,max_length=80)
    price = models.CharField(null=True,blank=True,max_length=80)
    status = models.BooleanField(null=True,blank=True,default=False)
    belong_user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True,related_name='pay_user')
    belong_art = models.ForeignKey(Article,on_delete=models.CASCADE,null=True,blank=True,related_name='pay_article')
    
    
    def __int__(self):
        return self.id