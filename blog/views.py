from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import F
from django.db import transaction
from .models import Category, Tag, Blog, Comment
from .serializers import CategorySerializer, TagSerializer, BlogSerializer, BlogDetailSerializer, CommentSerializer, CommentCreateSerializer
from .permissions import IsSuperUserOrReadOnly
from .pagination import BlogPageNumberPagination

# Create your views here.

class CategoryViewSet(viewsets.ModelViewSet):
    """
    分类视图集
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsSuperUserOrReadOnly]

    @action(detail=True, methods=['get'])
    def blogs(self, request, pk=None):
        category = self.get_object()
        blogs = Blog.objects.filter(category=category)
        serializer = BlogSerializer(blogs, many=True)
        return Response(serializer.data)

class TagViewSet(viewsets.ModelViewSet):
    """
    标签视图集
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsSuperUserOrReadOnly]

    @action(detail=True, methods=['get'])
    def blogs(self, request, pk=None):
        tag = self.get_object()
        blogs = Blog.objects.filter(tags=tag)
        serializer = BlogSerializer(blogs, many=True)
        return Response(serializer.data)

class BlogViewSet(viewsets.ModelViewSet):
    """
    博客视图集
    """
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [IsSuperUserOrReadOnly]
    pagination_class = BlogPageNumberPagination

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BlogDetailSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        queryset = Blog.objects.all()
        
        # 按分类筛选
        category_id = self.request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # 按标签筛选
        tag_id = self.request.query_params.get('tag', None)
        if tag_id:
            queryset = queryset.filter(tags__id=tag_id)
        
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
    def toggle_top(self, request, pk=None):
        """
        切换博客置顶状态
        """
        blog = self.get_object()
        if not request.user.is_superuser:
            return Response(
                {'detail': '只有超级用户可以执行此操作'},
                status=status.HTTP_403_FORBIDDEN
            )
        blog.is_top = not blog.is_top
        blog.save()
        return Response({
            'status': 'success',
            'message': '博客已置顶' if blog.is_top else '已取消置顶',
            'is_top': blog.is_top
        })

    @action(detail=False, methods=['get'])
    def hot(self, request):
        hot_blogs = self.get_queryset().order_by('-view_count')[:10]
        serializer = self.get_serializer(hot_blogs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def latest(self, request):
        latest_blogs = self.get_queryset().order_by('-created_at')[:10]
        serializer = self.get_serializer(latest_blogs, many=True)
        return Response(serializer.data)

class CommentViewSet(viewsets.ModelViewSet):
    """
    评论视图集
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        获取评论列表
        """
        # 如果是获取列表，需要指定 blog_id
        if self.action == 'list':
            blog_id = self.request.query_params.get('blog_id')
            if blog_id:
                return Comment.objects.filter(blog_id=blog_id).order_by('-time')
            return Comment.objects.none()
        # 如果是其他操作（如删除），返回所有评论
        return Comment.objects.all()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        创建评论
        """
        serializer = CommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            # 获取验证后的数据
            blog = serializer.validated_data['blog']
            content = serializer.validated_data['content']
            parent_comment_id = serializer.validated_data.get('parent_comment_id')
            
            # 创建评论
            comment = Comment.objects.create(
                user=request.user,
                blog=blog,
                content=content,
                parent_comment_id=parent_comment_id
            )
            
            # 更新博客的评论计数
            blog.comment_count = F('comment_count') + 1
            blog.save()
            
            # 返回完整的评论数据
            return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """
        删除评论
        """
        comment = self.get_object()
        
        # 检查是否是评论作者或超级用户
        if not (request.user == comment.user or request.user.is_superuser):
            return Response(
                {'detail': '只有评论作者或超级用户可以删除评论'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 更新博客的评论计数
        blog = comment.blog
        blog.comment_count = F('comment_count') - 1
        blog.save()
        
        # 删除评论
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

