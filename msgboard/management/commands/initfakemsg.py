from django.core.management.base import BaseCommand
from django.utils import timezone
from msgboard.models import Message, Reply
from bloguser.models import BlogUser
import random


class Command(BaseCommand):
    help = '初始化一些假留言数据'

    def handle(self, *args, **options):
        # 获取所有用户
        users = list(BlogUser.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR('没有找到用户, 请先创建用户'))
            return

        # 一些示例留言内容
        message_contents = [
            '博主写得太好了, 学习了!',
            '这篇文章对我帮助很大, 感谢分享!',
            '期待更多优质内容!',
            '写得非常详细, 赞一个!',
            '这个思路很新颖, 学习了!',
            '感谢博主的分享, 受益匪浅!',
            '文章写得很好, 继续加油!',
            '这个解决方案很实用, 学习了!',
            '期待博主更新更多内容!',
            '写得非常专业, 学习了!'
        ]

        # 一些示例回复内容
        reply_contents = [
            '谢谢支持!',
            '感谢你的留言!',
            '欢迎常来交流!',
            '谢谢夸奖, 我会继续努力!',
            '感谢你的建议!',
            '欢迎继续关注!',
            '谢谢你的支持!',
            '感谢你的留言, 我会继续分享!',
            '欢迎继续交流!',
            '谢谢你的鼓励!'
        ]

        # 创建5条主留言
        for _ in range(5):
            # 随机选择一个用户
            user = random.choice(users)
            # 随机选择一条留言内容
            content = random.choice(message_contents)
            # 创建主留言
            message = Message.objects.create(
                user=user,
                content=content
            )
            self.stdout.write(self.style.SUCCESS(f'创建主留言: {content}'))

            # 为每条主留言创建2-4条直接回复
            for _ in range(random.randint(2, 4)):
                # 随机选择一个用户
                reply_user = random.choice(users)
                # 随机选择一条回复内容
                reply_content = random.choice(reply_contents)
                # 创建直接回复
                reply = Reply.objects.create(
                    user=reply_user,
                    content=reply_content,
                    message=message
                )
                self.stdout.write(self.style.SUCCESS(f'创建直接回复: {reply_content}'))

                # 为每条直接回复创建1-2条子回复
                for _ in range(random.randint(1, 2)):
                    # 随机选择一个用户
                    child_user = random.choice(users)
                    # 随机选择一条回复内容
                    child_content = random.choice(reply_contents)
                    # 创建子回复
                    child_reply = Reply.objects.create(
                        user=child_user,
                        content=child_content,
                        message=message,
                        parent_reply=reply
                    )
                    self.stdout.write(self.style.SUCCESS(f'创建子回复: {child_content}'))

        self.stdout.write(self.style.SUCCESS('成功创建假留言数据!')) 