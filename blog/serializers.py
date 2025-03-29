from rest_framework import serializers
from .models import Category, Tag, Blog

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