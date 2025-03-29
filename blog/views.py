from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import F
from .models import Category, Tag, Blog
from .serializers import CategorySerializer, TagSerializer, BlogSerializer
from .permissions import IsSuperUserOrReadOnly
from .pagination import BlogPageNumberPagination

# Create your views here.

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsSuperUserOrReadOnly]

    @action(detail=True, methods=['get'])
    def blogs(self, request, pk=None):
        category = self.get_object()
        blogs = Blog.objects.filter(category=category, status='published')
        serializer = BlogSerializer(blogs, many=True)
        return Response(serializer.data)

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsSuperUserOrReadOnly]

    @action(detail=True, methods=['get'])
    def blogs(self, request, pk=None):
        tag = self.get_object()
        blogs = Blog.objects.filter(tags=tag, status='published')
        serializer = BlogSerializer(blogs, many=True)
        return Response(serializer.data)

class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [IsSuperUserOrReadOnly]
    pagination_class = BlogPageNumberPagination

    def get_queryset(self):
        queryset = Blog.objects.exclude(status='draft').all()
        
        # 按分类筛选
        category_id = self.request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # 按标签筛选
        tag_id = self.request.query_params.get('tag', None)
        if tag_id:
            queryset = queryset.filter(tags__id=tag_id)
        
        # 按状态筛选(超级用户可以查看所有状态)
        status = self.request.query_params.get('status', None)
        if status:
            if status == 'draft' and not self.request.user.is_superuser:
                return Blog.objects.none()  # 非超级用户请求草稿状态时返回空
            queryset = queryset.filter(status=status)
        
        return queryset.select_related('category').prefetch_related('tags')

    def retrieve(self, request, *args, **kwargs):
        """
        重写 retrieve 方法, 在获取文章详情时自动增加阅读量
        """
        instance = self.get_object()
        # 增加阅读量
        Blog.objects.filter(id=instance.id).update(view_count=F('view_count') + 1)
        # 重新获取更新后的实例
        instance.refresh_from_db()
        # 序列化并返回数据
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        blog = self.get_object()
        blog.like_count = F('like_count') + 1
        blog.save()
        return Response({'status': 'success'})

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        blog = self.get_object()
        if not request.user.is_superuser:
            return Response(
                {'detail': '只有超级用户可以执行此操作'},
                status=status.HTTP_403_FORBIDDEN
            )
        blog.status = 'published'
        blog.save()
        return Response({'status': 'success'})

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        blog = self.get_object()
        if not request.user.is_superuser:
            return Response(
                {'detail': '只有超级用户可以执行此操作'},
                status=status.HTTP_403_FORBIDDEN
            )
        blog.status = 'archived'
        blog.save()
        return Response({'status': 'success'})

    @action(detail=False, methods=['get'])
    def hot(self, request):
        hot_blogs = self.get_queryset().order_by('-view_count')[:10]
        serializer = self.get_serializer(hot_blogs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def latest(self, request):
        latest_blogs = self.get_queryset().order_by('-published_at')[:10]
        serializer = self.get_serializer(latest_blogs, many=True)
        return Response(serializer.data)

