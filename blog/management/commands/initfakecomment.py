from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from blog.models import Blog, Comment
from faker import Faker
import random

User = get_user_model()
fake = Faker(['zh_CN'])

class Command(BaseCommand):
    help = '为博客添加虚假的评论数据'

    def handle(self, *args, **options):
        # 获取所有博客
        blogs = Blog.objects.all()
        if not blogs.exists():
            self.stdout.write(self.style.ERROR('没有找到任何博客'))
            return

        # 获取所有用户
        users = User.objects.all()
        if not users.exists():
            self.stdout.write(self.style.ERROR('没有找到任何用户'))
            return

        # 为每篇博客添加评论
        for blog in blogs:
            # 随机生成5-15条评论
            comment_count = random.randint(5, 15)
            comments = []
            
            for _ in range(comment_count):
                # 随机选择一个用户
                user = random.choice(users)
                
                # 随机决定是否是回复
                is_reply = random.choice([True, False])
                parent_comment = None
                
                if is_reply and comments:
                    # 如果是回复，随机选择一条已存在的评论作为父评论
                    parent_comment = random.choice(comments)
                
                # 创建评论
                comment = Comment.objects.create(
                    user=user,
                    content=fake.text(max_nb_chars=200),
                    blog=blog,
                    parent_comment=parent_comment
                )
                comments.append(comment)
            
            # 更新博客的评论计数
            blog.comment_count = len(comments)
            blog.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'成功为博客 "{blog.title}" 添加了 {comment_count} 条评论')
            ) 