
from rest_framework import serializers
from goods.models import GoodsCategory, Goods, HotSearchWords, GoodsImages, Banner
from goods.models import GoodsCategoryBrand, IndexAd
from django.db.models import Q


# 一类目录
class GoodCategorySerializer3(serializers.ModelSerializer):
    """
    商品类别序列化
    """
    class Meta:
        model = GoodsCategory
        # 将fields属性设置为特殊属性'all'，以指示应使用模型中的所有字段
        fields = "__all__"


# 二类目录
class GoodCategorySerializer2(serializers.ModelSerializer):
    # sub_cat是在model中related_name设置的，相当于取的是父类
    sub_cat = GoodCategorySerializer3(many=True)

    class Meta:
        model = GoodsCategory
        fields = "__all__"


# 三类目录
class GoodCategorySerializer(serializers.ModelSerializer):
    sub_cat = GoodCategorySerializer2(many=True)

    class Meta:
        model = GoodsCategory
        fields = "__all__"


class GoodsImageSerializer(serializers.ModelSerializer):
    """
    轮播图序列化
    """
    class Meta:
        model = GoodsImages
        fields = ("image", )


class GoodsSerializer(serializers.ModelSerializer):
    """
    商品序列化
    """
    # 将商品类别信息加进来  注意此处的category要与model中的related_name相同
    category = GoodCategorySerializer()
    # 商品详情加上轮播图的图片
    images = GoodsImageSerializer(many=True)

    class Meta:
        model = Goods
        fields = "__all__"


class HotWordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotSearchWords
        fields = "__all__"
    

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = "__all__"


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategoryBrand
        fields = "__all__"


class IndexCategorySerializer(serializers.ModelSerializer):
    brands = BrandSerializer(many=True)
    goods = serializers.SerializerMethodField()
    sub_cat = GoodCategorySerializer2(many=True)
    ad_goods = serializers.SerializerMethodField()

    def get_ad_goods(self, obj):
        goods_json = {}
        ad_goods = IndexAd.objects.filter(category_id=obj.id, )
        if ad_goods:
            good_ins = ad_goods[0].goods
            goods_json = GoodsSerializer(good_ins, many=False, context={'request': self.context['request']}).data
        return goods_json

    def get_goods(self, obj):
        all_goods = Goods.objects.filter(Q(category_id=obj.id)|Q(category__parent_category_id=obj.id)|Q(category__parent_category__parent_category_id=obj.id))
        goods_serializer = GoodsSerializer(all_goods, many=True, context={'request': self.context['request']})
        return goods_serializer.data

    class Meta:
        model = GoodsCategory
        fields = "__all__"

