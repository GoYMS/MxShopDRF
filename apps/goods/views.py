from goods.serializers import GoodCategorySerializer, GoodsSerializer, HotWordsSerializer
from goods.serializers import BannerSerializer, IndexCategorySerializer
from goods.filters import GoodsFilter
from goods.models import GoodsCategory, Banner
from goods.models import Goods, HotSearchWords
from rest_framework import viewsets
from rest_framework import mixins
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class GoodsPagination(PageNumberPagination):
    page_size = 12  # 一页的个数
    page_size_query_param = 'page_size'
    page_query_param = "page"  # url的名称
    max_page_size = 100


class GoodsListViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    商品列表页, 分页， 搜索， 过滤， 排序
    """
    # 所有信息
    queryset = Goods.objects.all()
    # 序列化
    serializer_class = GoodsSerializer
    # 分页
    pagination_class = GoodsPagination
    # 添加过滤器
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    # 指定过滤器
    filter_class = GoodsFilter
    # 查询
    search_fields = ('name', 'goods_brief', 'goods_desc')
    # 排序
    ordering_fields = ('sold_num', 'shop_price')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.click_num +=  1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


# mixins.RetrieveModelMixin是可以在url后边加上商品的序号可以查看详情的信息
class CategoryViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    list:
        商品分类列表数据
    retrieve:
        获取商品的全部信息
    """
    queryset = GoodsCategory.objects.filter(category_type=1)
    serializer_class = GoodCategorySerializer


class HotSearchsViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    获取热搜词列表
    """
    queryset = HotSearchWords.objects.all().order_by("-index")
    serializer_class = HotWordsSerializer


class BannersViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    获取轮播图
    """
    queryset = Banner.objects.all().order_by("index")
    serializer_class = BannerSerializer


class IndexCategoryViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    首页商品分类数据
    """
    queryset = GoodsCategory.objects.filter(is_tab=True, name__in=["生鲜食品", "酒水饮料"])
    serializer_class = IndexCategorySerializer
