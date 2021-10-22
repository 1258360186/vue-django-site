import os
from blog_site.settings import ALLOWED_HOSTS
from time import strftime
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from blog.models import Article,Userinfo,Lanmu,Pinglun,PayOrder,Favourite,Like
from django.contrib.auth.models import User,Group,Permission,ContentType
from django.contrib.auth.hashers import check_password,make_password
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from  PIL import Image
from io import BytesIO
import datetime
import base64
import re
import requests
import json

HOST = "http://118.178.124.82:80/"



@api_view(['POST','PUT'])
def add_article(request):
    if request.method == "PUT":
        token = request.POST['token']
        perm=['blog.change_articl']
        check = checklogin(token,perm)
        if check !='pass':
            return Response(check)
        
        lanmuid = request.POST['lanmuid']
        articleid = request.POST['articleid']
        lanmu = Lanmu.objects.get(id=lanmuid)
        article = Article.objects.get(id=articleid)
        article.belong_lanmu = lanmu
        article.save()
        return Response('ok')
    
    title = request.POST['title']
    describe = request.POST['describe']
    cover = request.POST['cover']
    content = request.POST['content']
    token = request.POST['token']
    
    user_token = Token.objects.filter(key=token)
    if len(user_token)==0:
        return Response('notoken')
    if len(title)==0:
        return Response('notitle')
    
    new_article = Article(title=title,describe=describe)
    new_article.save()
    
    pattern = re.compile(r'src="(.*?)"')   
    imgLIst = pattern.findall(content)
    for idx,imgurl in enumerate(imgLIst) :
        if('http'in imgurl):
            response = requests.get(imgurl)
            img = Image.open(BytesIO(response.content))
            imgname = datetime.datetime.now().strftime('%Y%m%d%H%M%S') +'-'+ str(new_article.id) +'-'+ str(idx+1)
            img.save('upload/'+imgname+'.png')
            src = HOST+'upload/'+imgname+'.png'
            content = content.replace(imgurl, src)
        else:
              img = base64.b64decode(imgurl.split(',')[1])
              imgg = re.search( r'/(.*?);', imgurl, re.M|re.I).group(1)
              imgname = datetime.datetime.now().strftime('%Y%m%d%H%M%S') +'-'+ str(new_article.id) +'-'+ str(idx+1)+'.'+imgg
              upload = os.path.join('upload',imgname).replace('\\','/')
              src = HOST+upload
              content = content.replace(imgurl, src)
              with open(upload,'wb') as f:
                  f.write(img)
    cover_img = base64.b64decode(cover.split(',')[1])
    cover_imgg = re.search( r'/(.*?);', cover, re.M|re.I).group(1)
    cover_imgname = datetime.datetime.now().strftime('%Y%m%d%H%M%S') +'-'+ str(new_article.id) +'-0.'+cover_imgg
    cover_upload = os.path.join('upload',cover_imgname).replace('\\','/')
    cover_src = HOST+cover_upload
    with open(cover_upload,'wb') as f:
        f.write(cover_img)
    new_article.content = content
    new_article.cover = cover_src
    new_article.belong = user_token[0].user
    new_article.save()
    return Response('ok')


@api_view(['POST'])
def baiyu_login(request):
    
    username = request.POST['username']
    password = request.POST['password']
    user = User.objects.filter(username=username)
    if user:
        checkpwd = check_password(password,user[0].password)
        if checkpwd:
            user_info = Userinfo.objects.get(belong=user[0])
            token = Token.objects.get_or_create(user=user[0])
            token = Token.objects.get(user=user[0])
        else:
            return Response('pwderror')
    else:
          return Response('none')
    
    user_info = {
        'token':token.key,
        'nickname':user_info.nickName ,
        'headImg':user_info.headImg 
    }
    return Response(user_info)


@api_view(['POST'])
def baiyu_register(request):
    username = request.POST['username']
    password = request.POST['password']
    password2 = request.POST['password2']
    
    user = User.objects.filter(username=username)
    if user:
        return Response('usererror')
    else:
        new_password = make_password(password,username)
        newUser = User(username=username,password=new_password)
        newUser.save()
    token = Token.objects.get_or_create(user=newUser)
    token = Token.objects.get(user=newUser)
    userinfo = Userinfo.objects.get_or_create(belong=newUser)
    userinfo = Userinfo.objects.get(belong=newUser)
    user_info = {
        'token':str(token),
        'nickname':userinfo.nickName,
        'headImg':userinfo.headImg
    }
    return Response(user_info)


@api_view(['POST'])
def auto_login(request):
    token = request.POST['token']
    user_token = Token.objects.filter(key=token)[0]
    if user_token:
        # print(user_token)
        userinfo = Userinfo.objects.get(belong=user_token.user)
        user_info = {
            'token':str(token),
            'nickname':userinfo.nickName,
            'headImg':userinfo.headImg
        }
        return Response(user_info)
    else:
        return Response('tokenerror')

@api_view(['POST'])
def baiyu_logout(request):
    token = request.POST['token']
    user_token = Token.objects.get(key=token)
    user_token.delete()
    return Response('ok')

@api_view(['GET'])
def article_list(request):
    page = request.GET['page']
    pagesize = request.GET['pagesize']
    lanmu = request.GET['lanmu']
    
    if lanmu=='all':
        articles = Article.objects.all()
    elif lanmu=='nobeleng':
        articles = Article.objects.filter(belong_lanmu=None)
    else:
        articles = Article.objects.filter(belong_lanmu__name=lanmu)
    total = len(articles)
    paginator = Paginator(articles,pagesize)
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    articles_list=[]
    for _ in articles:
        item = {
            'title':_.title,
            'cover':_.cover,
            'describe':_.describe,
            'nickname':'',
            'id':_.id
        }
        article_user = _.belong
        user_info = Userinfo.objects.filter(belong=article_user)[0]
        if user_info:
            item['nickname'] = user_info.nickName
        else:
            item['nickname'] = article_user.username
        articles_list.append(item)
    return Response({'data':articles_list,'total':total})

@api_view(['DELETE'])
def delete_article(request):
    id = request.POST['id']
    token = request.POST['token']
    print(token)
    user_token = Token.objects.filter(key=token)
    if len(user_token)==0:
        return Response('nologin')
    
    user = user_token[0].user
    user_perm = user.has_perm('blog.delete_article')
    if user_perm==False:
        return Response('noperm')
    print(user_perm)
    article = Article.objects.get(id=id)
    article.delete()
    return Response('ok')

@api_view(['POST'])
def user_permisson(request):
    token = request.POST['token']
    content_type = request.POST['contentType']
    permissions = json.loads(request.POST['permissions'])
    user_token = Token.objects.filter(key=token)
    if len(user_token)==0:
        return Response('nologin')
    user = user_token[0].user
    for op in permissions:
        op = content_type.split('_')[0]+'.'+op+'_'+content_type.split('_')[1]
        check = user.has_perm(op)
        if check==False:
            return Response('noperm')
    return Response('ok')

@api_view(['GET','POST',"PUT","DELETE"])
def baiyu_newgroup(request):
    if request.method == "POST":
        token = request.POST['token']
        perm=['auth.add_user','auth.delete_user','auth.change_user','auth.view_user']
        check = checklogin(token,perm)
        if check !='pass':
            return Response(check)
        
        group = request.POST['group']
        choose = json.loads(request.POST['choose'])
        # print(request.POST['choose'])
        group = Group.objects.get(name=group)
        # print(groups)
        for user in choose:
            user = User.objects.get(username=user)
            # user.groups.add(group)
            group.user_set.add(user)
        return Response('ok')
    
    if request.method == "DELETE":
        token = request.POST['token']
        name = request.POST['name']
        perm=['auth.add_user','auth.delete_user','auth.change_user','auth.view_user']
        check = checklogin(token,perm)
        if check !='pass':
            return Response(check)
        groups = Group.objects.get(name=name)
        groups.delete()
        return Response('ok')
        
    if request.method == "GET":
        groups = Group.objects.all()
        grouplist=[]
        for g in groups:
            item={
                'name':g.name
            }
            grouplist.append(item)
        return Response(grouplist)
    if request.method == "PUT":
        token = request.POST['token']
        perm=['auth.add_user','auth.delete_user','auth.change_user','auth.view_user']
        check = checklogin(token,perm)
        if check !='pass':
            return Response(check)
        name = request.POST['newgroupname']
        permlist = json.loads(request.POST['permlist'])
        new_group = Group.objects.filter(name=name)
        if new_group:
            return Response('same')
        new_group = Group.objects.create(name=name)
        for perm in permlist:
            app = perm['contentType'].split('_')[0]
            model = perm['contentType'].split('_')[1]
            contenttype = ContentType.objects.get(app_label=app,model=model)
            for op in perm['permsop']:
                op=op+'_'+model
                permission = Permission.objects.get(content_type=contenttype,codename=op)
                new_group.permissions.add(permission)
            return Response('ok')
    
def checklogin(token,perm):
    user_token = Token.objects.filter(key=token)
    if user_token:
        user = user_token[0].user
        for op in perm:
            check=user.has_perm(op)
            if check:
                return 'pass'
            else:
                return 'error'
    else:
      return 'nologin'
  
  
@api_view(['GET'])
def baiyu_userlist(request):
    users = User.objects.all()
    userlist=[]
    for u in users:
        item={
            'name':u.username
        }
        userlist.append(item)
    print(userlist)
    return Response(userlist)


@api_view(['GET','POST',"PUT","DELETE"])
def baiyu_lanmu(request):
    if request.method == "DELETE":
        token = request.POST['token']
        id = request.POST['id']
        perm=['blog.delete_lanmu']
        check = checklogin(token,perm)
        if check !='pass':
            return Response(check)
        lanmu = Lanmu.objects.get(id=id)
        lanmu.delete()
        return Response('ok')
    
    if request.method == "GET":
        lanmus = Lanmu.objects.filter(belong=None)
        data = loopgetlanmu(lanmus)
        return Response(data)
    if request.method == "POST":
        token = request.POST['token']
        perm=['blog.add_lanmu','blog.delete_lanmu','blog.change_lanmu','blog.view_lanmu']
        check = checklogin(token,perm)
        if check !='pass':
            return Response(check)
        lanmutree = json.loads(request.POST['lanmutree'])
        # print(lanmutree)
        loopsavelanmu(lanmutree,None)
        
        return Response('ok')


def loopgetlanmu(lanmulist):
    lanmudata=[]
    for lanmu in lanmulist:
        item = {
            'id':lanmu.id,
            'label':lanmu.name,
            'children':[],
            'articlenum':len(lanmu.article_lanmu.all())
        }
        children = lanmu.lanmu_child.all()
        if children:
            childrendata = loopgetlanmu(children)
            for c in childrendata:
                item["children"].append(c)
        lanmudata.append(item)
    return lanmudata
        

def loopsavelanmu(tree,id):
    parents = Lanmu.objects.filter(id=id)
    if parents:
        for stree in tree:
            savelanmu = Lanmu.objects.filter(id=stree['id'])
            if savelanmu:
                savelanmu[0].belong=parents[0]
                savelanmu[0].save()
                if len(stree['children'])>0:
                    
                    loopsavelanmu(stree['children'],savelanmu[0].id)
            else:
                newlanmu = Lanmu(name=stree['label'],belong=parents[0])
                newlanmu.save()
                if len(stree['children'])>0:
                    loopsavelanmu(stree['children'],newlanmu.id)
    else:
        for stree in tree:
            savelanmu = Lanmu.objects.filter(id=stree['id'])
            if savelanmu:
                savelanmu[0].belong=None
                savelanmu[0].save()
                loopsavelanmu(stree['children'],savelanmu[0].id)
            else:
                newlanmu = Lanmu(name=stree['label'])
                newlanmu.save()
                if(len(stree['children'])>0):
                    loopsavelanmu(stree['children'],newlanmu.id)

    return


@api_view(['GET'])
def baiyu_article(request):
    if request.method == "GET":
        id = request.GET["id"]
        article = Article.objects.get(id=id)
        data={
            'title':article.title,
            'cover':article.cover,
            'describe':article.describe,
            'content':article.content,
            'nickname':article.belong.username,
            'lanmu':'',
            'pre':0,
            'next':0
        }
        pre = Article.objects.filter(id__lt=id)
        if pre:
            data['pre'] = pre.last().id
        next = Article.objects.filter(id__gt=id)
        if next:
            data['next'] = next.first().id
        if article.belong_lanmu:
            data['lanmu'] = article.belong_lanmu.name
        return Response(data)
   
@api_view(['GET',"POST"])
def baiyu_pinglun(request):
    if request.method == "GET": 
        id = request.GET['id']
        pagesize = request.GET['size']
        page = request.GET['page']
        
        article = Article.objects.get(id=id)
        pingluns = Pinglun.objects.filter(belong_art=article)[::-1]
        
        
        total = len(pingluns)
        paginator = Paginator(pingluns,pagesize)
        try:
            pingluns = paginator.page(page)
        except PageNotAnInteger:
            pingluns = paginator.page(1)
        except EmptyPage:
            pingluns = paginator.page(paginator.num_pages)
        pingluns_list=[]
        for _ in pingluns:
            item = {
                
                'nickname':'',
                'text':_.text
            }
            article_user = _.belong_user
            user_info = Userinfo.objects.filter(belong=article_user)[0]
            if user_info:
                item['nickname'] = user_info.nickName
            else:
                item['nickname'] = article_user.username
            pingluns_list.append(item)
        return Response({'data':pingluns_list,'total':total})
        
        
        
    if request.method == "POST": 
        try:
            token = request.POST['token']
        except :
            return Response('nologin')
        perm=['blog.view_article']
        check = checklogin(token,perm)
        if check !='pass':
            return Response(check)
        id = request.POST['id']
        text = request.POST['text']
        
        article = Article.objects.get(id=id)
        user = Token.objects.get(key=token).user
        
        newpinglun = Pinglun(belong_user=user,belong_art=article,text=text)
        newpinglun.save()
        return Response('ok')
    
@api_view(['GET',"POST"])
def baiyu_userarticle(request):
    if request.method == "POST": 
        token = request.POST['token']
        id = request.POST['id']
        user = Token.objects.get(key=token).user
        article = Article.objects.get(id=id)
        info={
            'like':False,
            'favor':False,
            'mon':False
        }
        
        like = Like.objects.filter(belong_user=user,belong_art=article)
        if like:
            info['like'] = True
        favourite = Favourite.objects.filter(belong_user=user,belong_art=article)
        if favourite:
            info['favor'] = True
        payed = PayOrder.objects.filter(belong_user=user,belong_art=article,status=True)
        if payed:
            info['mon'] = True
            
        
        return Response(info)
    
    

@api_view(["POST"])
def baiyu_articlelike(request):
    print(request)
    if request.method == "POST": 
        token = request.POST['token']
        token = Token.objects.filter(key=token)
        if len(token)==0:
            return Response('nolgin')
        id = request.POST['id']
        user = token[0].user
        article = Article.objects.get(id=id)
        like = Like.objects.filter(belong_user=user,belong_art=article)
        if like:
            like[0].delete()
            return Response('ok')
        else:
            new= Like(belong_user=user,belong_art=article)
            new.save()
            return Response('ok')
        
        
@api_view(["POST"])
def baiyu_articlefavor(request):
    if request.method == "POST": 
        token = request.POST['token']
        token = Token.objects.filter(key=token)
        if len(token)==0:
            return Response('nolgin')
        id = request.POST['id']
        user = token[0].user
        article = Article.objects.get(id=id)
        favour = Favourite.objects.filter(belong_user=user,belong_art=article)
        if favour:
            favour[0].delete()
            return Response('ok')
        else:
            new= Favourite(belong_user=user,belong_art=article)
            new.save()
            return Response('ok')