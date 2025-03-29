from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='分类名称')
    description = models.TextField(blank=True, verbose_name='分类描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='URL标识')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children', verbose_name='父分类')
    order = models.IntegerField(default=0, verbose_name='排序')

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = verbose_name
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='标签名称')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='URL标识')
    description = models.TextField(blank=True, verbose_name='标签描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Blog(models.Model):
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('published', '已发布'),
        ('archived', '已归档'),
    )

    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    summary = models.TextField(blank=True, verbose_name='摘要')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='blogs', verbose_name='分类')
    tags = models.ManyToManyField(Tag, related_name='blogs', blank=True, verbose_name='标签')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    is_top = models.BooleanField(default=False, verbose_name='是否置顶')
    view_count = models.PositiveIntegerField(default=0, verbose_name='浏览次数')
    like_count = models.PositiveIntegerField(default=0, verbose_name='点赞数')
    comment_count = models.PositiveIntegerField(default=0, verbose_name='评论数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='发布时间')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='URL标识')
    cover_image = models.ImageField(upload_to='blog/covers/', null=True, blank=True, verbose_name='封面图片')
    is_original = models.BooleanField(default=True, verbose_name='是否原创')
    original_url = models.URLField(blank=True, verbose_name='原文链接')

    class Meta:
        verbose_name = '博客'
        verbose_name_plural = verbose_name
        ordering = ['-is_top', '-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)