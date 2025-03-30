from rest_framework import serializers
from .models import Category, Tag, Blog, Comment
from bloguser.serializers import UserModelSerializer

class CommentSerializer(serializers.ModelSerializer):
    """
    评论序列化器
    """
    user = UserModelSerializer(read_only=True)
    reply_to = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'time', 'content', 'parent_comment', 'reply_to']
        read_only_fields = ['id', 'time']

    def get_reply_to(self, obj):
        """
        获取回复对象的用户名
        """
        if obj.parent_comment:
            return obj.parent_comment.user.name
        return None

class CommentCreateSerializer(serializers.ModelSerializer):
    """
    评论创建序列化器
    """
    blog_id = serializers.IntegerField(required=True)
    content = serializers.CharField(required=True, min_length=10, error_messages={
        'min_length': '评论内容不能少于10个字'
    })
    parent_comment_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Comment
        fields = ['blog_id', 'content', 'parent_comment_id']

    def validate(self, attrs):
        """
        验证数据
        """
        # 验证博客是否存在
        blog_id = attrs.get('blog_id')
        try:
            blog = Blog.objects.get(id=blog_id)
        except Blog.DoesNotExist:
            raise serializers.ValidationError({'blog_id': '博客不存在'})

        # 如果指定了父评论，验证父评论是否存在且属于同一博客
        parent_comment_id = attrs.get('parent_comment_id')
        if parent_comment_id:
            try:
                parent_comment = Comment.objects.get(id=parent_comment_id, blog=blog)
            except Comment.DoesNotExist:
                raise serializers.ValidationError({'parent_comment_id': '父评论不存在'})
            
        attrs['blog'] = blog

        return attrs

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'slug', 'parent', 'order', 'created_at', 'updated_at']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'description', 'created_at', 'updated_at']

class BlogSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Blog
        fields = [
            'id', 'title', 'content', 'summary', 'category', 'tags',
            'category_id', 'tag_ids', 'status', 'is_top', 'view_count',
            'like_count', 'comment_count', 'created_at', 'updated_at',
            'published_at', 'slug', 'cover_image', 'is_original', 'original_url'
        ]
        read_only_fields = [
            'view_count', 'like_count', 'comment_count',
            'created_at', 'updated_at', 'published_at', 'slug'
        ]

    def create(self, validated_data):
        tag_ids = validated_data.pop('tag_ids', [])
        category_id = validated_data.pop('category_id')
        
        # 设置分类
        validated_data['category_id'] = category_id
        
        # 创建博客
        blog = super().create(validated_data)
        
        # 设置标签
        if tag_ids:
            blog.tags.set(tag_ids)
        
        return blog

    def update(self, instance, validated_data):
        tag_ids = validated_data.pop('tag_ids', None)
        category_id = validated_data.pop('category_id', None)
        
        # 更新分类
        if category_id:
            instance.category_id = category_id
        
        # 更新博客
        blog = super().update(instance, validated_data)
        
        # 更新标签
        if tag_ids is not None:
            blog.tags.set(tag_ids)
        
        return blog

class BlogDetailSerializer(BlogSerializer):
    """
    博客详情序列化器
    """
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = BlogSerializer.Meta.fields + ['comments']

    def get_comments(self, obj):
        """
        获取所有评论, 包括对博客的评论和对评论的回复
        """
        return CommentSerializer(obj.comments.all().order_by('-time'), many=True).data 