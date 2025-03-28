from django.core.management.base import BaseCommand
from welcome.models import Welcome, Description


class Command(BaseCommand):
    help = '初始化欢迎页面数据'

    def handle(self, *args, **options):
        # 检查是否已存在Welcome数据
        if Welcome.objects.exists():
            self.stdout.write(self.style.WARNING('欢迎页面数据已存在，正在重新初始化...'))
            # 清空现有数据
            Welcome.objects.all().delete()
        else:
            self.stdout.write(self.style.SUCCESS('开始初始化欢迎页面数据...'))

        # 创建Welcome数据
        welcome = Welcome.objects.create(
            title='HarryWebAI',
            buttonText='探索更多'
        )

        # 创建Description数据
        descriptions = [
            '锤炼意志',
            '锻造身体',
            '积累学识'
        ]

        for content in descriptions:
            Description.objects.create(
                content=content,
                welcome=welcome
            )

        self.stdout.write(self.style.SUCCESS('欢迎页面数据初始化成功！'))
        self.stdout.write(f'  - 标题: {welcome.title}')
        self.stdout.write(f'  - 按钮文本: {welcome.buttonText}')
        self.stdout.write('  - 描述信息:')
        for desc in Description.objects.filter(welcome=welcome):
            self.stdout.write(f'    * {desc.content}') 