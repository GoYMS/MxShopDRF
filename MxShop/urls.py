"""MxShop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
# drf 的自动生成文档的包
from rest_framework.documentation import include_docs_urls
from MxShop.settings import MEDIA_ROOT
from users.views import SmsCodeViewset, UserViewset
from django.views.static import serve
from django.conf.urls import url, include
from extra_apps import xadmin

# 关于router
from rest_framework.routers import DefaultRouter
from goods.views import CategoryViewset, GoodsListViewSet, HotSearchsViewset, BannersViewset
from goods.views import IndexCategoryViewset
from user_operation.views import UserFavViewset, LeavingMessageSerializerViewset, UserAddressViewset
# drf自带token
from rest_framework.authtoken import views
# jwt的token
from rest_framework_jwt.views import obtain_jwt_token
from trade.views import ShoppingCartViewset, OrderViewset
from trade.views import AlipayView
from django.views.generic import TemplateView


router = DefaultRouter()
# 配置category的url
router.register('categorys', CategoryViewset, basename='categorys')
# 配置搜索热门
router.register(r'hotsearchs', HotSearchsViewset, basename='hotsearchs')
# 配置goods的url
router.register('goods', GoodsListViewSet, basename='goods')
# 配置短信验证的url
router.register('code', SmsCodeViewset, basename='code')
# 配置用户注册
router.register('users', UserViewset, basename='users')
# 用户收藏
router.register('userfavs', UserFavViewset, basename='userfavs')
# 用户留言
router.register('messages', LeavingMessageSerializerViewset, basename='messages')
# 用户收货地址
router.register('address', UserAddressViewset, basename='address')
# 购物车
router.register('shopcarts', ShoppingCartViewset, basename='shopcarts')
# 订单
router.register('orders', OrderViewset, basename='orders')
# 轮播图
router.register('banners', BannersViewset, basename='banners')
# 首页商品系列数据
router.register(r'indexgoods', IndexCategoryViewset, basename="indexgoods")


urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^ueditor/', include('DjangoUeditor.urls')),
    # 如果不写这个在后台管理系统中找不到图片，就是显示一个残图
    # serve,处理静态文件的方法，其参数需要知道前边path的路径以及后边在哪个路径下边
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),
    # drf可浏览的api，就相当于可以打开drf的一个后台的路径
    url(r'^api-auth/', include('rest_framework.urls')),
    # 生成drf的自动文档的基本配置
    url(r'^docs/', include_docs_urls(title="幕学生鲜")),
    # router  上边的url要想运行，下边的就必须得加上
    url(r'^', include(router.urls)),
    # drf自带的token登录
    url(r'^api-token-auth/', views.obtain_auth_token),
    # jwt的token登录
    url(r'^login/$', obtain_jwt_token),
    # 配置支付的接口
    url(r'^alipay/return/', AlipayView.as_view(), name='alipay'),

    url(r'^index/', TemplateView.as_view(template_name="index.html"), name="index"),

    # 第三方登录
    url('', include('social_django.urls', namespace='social'))
]
