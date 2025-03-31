from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from blog.models import Category, Tag
from aboutme.models import WorkExperience, Education, Project, SkillCategory
from welcome.models import Welcome, Description

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

        # 创建工作经验示例数据
        self.stdout.write('创建工作经验示例数据...')
        try:
            work_experience = WorkExperience.objects.create(
                title='高级软件工程师',
                company='示例科技有限公司',
                period='2020-2023',
                achievements=['负责核心系统的开发和维护', '带领团队完成多个重要项目']
            )
            self.stdout.write(self.style.SUCCESS(f'成功创建工作经验: {work_experience.title}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'创建工作经验失败: {str(e)}'))

        # 创建教育经历示例数据
        self.stdout.write('创建教育经历示例数据...')
        try:
            education = Education.objects.create(
                major='计算机科学与技术',
                school='示例大学',
                period='2016-2020',
                degree='学士',
                description='主修计算机科学与技术，获得优秀毕业生称号'
            )
            self.stdout.write(self.style.SUCCESS(f'成功创建教育经历: {education.major}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'创建教育经历失败: {str(e)}'))

        # 创建项目示例数据
        self.stdout.write('创建项目示例数据...')
        try:
            project = Project.objects.create(
                name='示例项目',
                techStack='Python, Django, React',
                details=['使用Django开发后端API', '使用React开发前端界面']
            )
            self.stdout.write(self.style.SUCCESS(f'成功创建项目: {project.name}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'创建项目失败: {str(e)}'))

        # 创建技能分类示例数据
        self.stdout.write('创建技能分类示例数据...')
        try:
            skill_category = SkillCategory.objects.create(
                name='编程语言',
                skills=['Python', 'JavaScript', 'Java']
            )
            self.stdout.write(self.style.SUCCESS(f'成功创建技能分类: {skill_category.name}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'创建技能分类失败: {str(e)}'))

        # 创建欢迎信息示例数据
        self.stdout.write('创建欢迎信息示例数据...')
        try:
            # 检查是否已存在欢迎信息
            if not Welcome.objects.exists():
                welcome = Welcome.objects.create(
                    title='欢迎访问',
                    buttonText='开始探索'
                )
                self.stdout.write(self.style.SUCCESS(f'成功创建欢迎信息: {welcome.title}'))

                # 创建欢迎信息的描述
                descriptions = [
                    '示例数据1',
                    '示例数据2',
                    '示例数据3'
                ]
                for content in descriptions:
                    Description.objects.create(
                        content=content,
                        welcome=welcome
                    )
                self.stdout.write(self.style.SUCCESS('成功创建欢迎信息描述'))
            else:
                self.stdout.write(self.style.WARNING('欢迎信息已存在，跳过创建'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'创建欢迎信息失败: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('系统初始化完成')) 