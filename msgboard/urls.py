from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessageViewSet

# 创建路由器
router = DefaultRouter()
# 注册视图集
router.register(r'messages', MessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
