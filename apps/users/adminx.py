
import xadmin
from xadmin import views
from .models import VerifyCode


# 设置主题
class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True


#  设置头部和尾部
class GlobalSettings(object):
    site_title = "慕学生鲜后台"
    site_footer = "mxshop"


class VerifyCodeAdmin(object):
    list_display = ['code', 'mobile', "add_time"]


xadmin.site.register(VerifyCode, VerifyCodeAdmin)
xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSettings)