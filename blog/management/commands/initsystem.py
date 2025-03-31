from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from blog.models import Category, Tag

User = get_user_model()

class Command(BaseCommand):
    help = '初始化系统数据，包括分类、标签和超级用户'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化系统数据...')

        # 创建分类
        self.stdout.write('创建分类...')
        try:
            category = Category.objects.create(
                name='示例分类',
                order=1
            )
            self.stdout.write(self.style.SUCCESS(f'成功创建分类: {category.name}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'创建分类失败: {str(e)}'))

        # 创建标签
        self.stdout.write('创建标签...')
        try:
            tag = Tag.objects.create(
                name='示例标签'
            )
            self.stdout.write(self.style.SUCCESS(f'成功创建标签: {tag.name}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'创建标签失败: {str(e)}'))

        # 创建超级用户
        self.stdout.write('创建超级用户...')
        try:
            if not User.objects.filter(email='harry.web.ai@gmail.com').exists():
                user = User.objects.create_superuser(
                    email='harry.web.ai@gmail.com',
                    password='111111',
                    name='HarryWebAI',
                    telephone='19812939717',
                    is_active=True
                )
                self.stdout.write(self.style.SUCCESS(f'成功创建超级用户: {user.name}'))
            else:
                # 如果用户已存在，确保其 is_active 为 True
                user = User.objects.get(email='harry.web.ai@gmail.com')
                if not user.is_active:
                    user.is_active = True
                    user.save()
                    self.stdout.write(self.style.SUCCESS('已激活超级用户'))
                self.stdout.write(self.style.WARNING('超级用户已存在，跳过创建'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'创建超级用户失败: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('系统初始化完成')) 