from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'tags', views.TagViewSet)
router.register(r'blogs', views.BlogViewSet, basename='blog')
router.register(r'comments', views.CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
]
