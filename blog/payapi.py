from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.FileItem import FileItem
from alipay.aop.api.domain.AlipayTradeAppPayModel import AlipayTradeAppPayModel
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.domain.AlipayTradePayModel import AlipayTradePayModel
from alipay.aop.api.domain.GoodsDetail import GoodsDetail
from alipay.aop.api.domain.SettleDetailInfo import SettleDetailInfo
from alipay.aop.api.domain.SettleInfo import SettleInfo
from alipay.aop.api.domain.SubMerchant import SubMerchant
from alipay.aop.api.request.AlipayOfflineMaterialImageUploadRequest import AlipayOfflineMaterialImageUploadRequest
from alipay.aop.api.request.AlipayTradeAppPayRequest import AlipayTradeAppPayRequest
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
from alipay.aop.api.request.AlipayTradePayRequest import AlipayTradePayRequest
from alipay.aop.api.response.AlipayOfflineMaterialImageUploadResponse import AlipayOfflineMaterialImageUploadResponse
from alipay.aop.api.response.AlipayTradePayResponse import AlipayTradePayResponse

from django.shortcuts import HttpResponse
from blog_site import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from blog.models import Article,PayOrder
import datetime
import random

@api_view(['POST'])
def getALipayurl(request):
    
    token = request.POST['token']
    token = Token.objects.filter(key=token)
    if len(token) == 0:
        return Response('nologin')
    user = token[0].user
    id = request.POST['id']
    article = Article.objects.get(id=id)
    
    nowtime = datetime.datetime.now()
    
    new = PayOrder(belong_user=user,belong_art=article)
    new.order =str(nowtime.year) + str(random.randrange(100000,999999))
    new.price = '9.9'
    new.save()
    
    
    alipay_client_config = AlipayClientConfig()
    alipay_client_config.server_url = settings.ALIPAY_URL
    alipay_client_config.app_id = settings.ALIPAY_APPID
    alipay_client_config.app_private_key = settings.APP_PRIVATE_KEY
    alipay_client_config.alipay_public_key = settings.ALIPAY_PUBLIC_KEY
    
    client = DefaultAlipayClient(alipay_client_config=alipay_client_config)
    model = AlipayTradePagePayModel()  # 创建网站支付模型
    model.out_trade_no = new_payorder.order
    model.total_amount = new_payorder.price
    model.subject = "打赏订单："+new_payorder.order+'/'+new_payorder.price+'元'
    model.product_code = 'FAST_INSTANT_TRADE_PAY'
    model.timeout_express = '5m'
    
    pay_request = AlipayTradePagePayRequest(biz_model=model)
    pay_request.notify_url = settings.ALIPAY_NOTIFY_URL
    pay_request.return_url = settings.ALIPAY_RETURN_URL
    response = client.page_execute(pay_request, http_method='GET')
    # print(response)
    pay_link = response
    return Response({'pay_link':pay_link})
    