from django.core.management.base import BaseCommand
from aboutme.models import WorkExperience, Education, Project, SkillCategory

class Command(BaseCommand):
    help = '初始化关于我的数据'

    def handle(self, *args, **options):
        # 清空现有数据
        WorkExperience.objects.all().delete()
        Education.objects.all().delete()
        Project.objects.all().delete()
        SkillCategory.objects.all().delete()

        # 创建工作经历
        work = WorkExperience.objects.create(
            title='全栈开发工程师',
            company='某科技公司',
            period='2022 - 至今',
            achievements=[
                '负责公司核心业务系统的开发和维护',
                '使用 Vue3 + TypeScript 开发前端应用',
                '使用 Node.js 开发后端服务'
            ]
        )
        self.stdout.write(self.style.SUCCESS(f'成功创建工作经历: {work}'))

        # 创建教育经历
        education = Education.objects.create(
            major='计算机科学与技术',
            school='某重点大学',
            period='2018 - 2022',
            degree='学士学位',
            description='主修课程：数据结构、算法分析、计算机网络、操作系统、数据库系统'
        )
        self.stdout.write(self.style.SUCCESS(f'成功创建教育经历: {education}'))

        # 创建项目经历
        project = Project.objects.create(
            name='个人博客系统',
            techStack='Vue3 + TypeScript + Element Plus',
            details=[
                '使用 Vue3 Composition API 开发',
                '实现了响应式设计和优雅的动画效果',
                '集成了 Markdown 编辑器和代码高亮'
            ]
        )
        self.stdout.write(self.style.SUCCESS(f'成功创建项目经历: {project}'))

        # 创建技能分类
        skill_categories = [
            {
                'name': '前端开发',
                'skills': ['Vue3', 'TypeScript', 'React', 'CSS3', 'HTML5']
            },
            {
                'name': '后端开发',
                'skills': ['Node.js', 'Express', 'MySQL', 'MongoDB']
            },
            {
                'name': '开发工具',
                'skills': ['Git', 'VS Code', 'Docker', 'Webpack']
            }
        ]

        for category_data in skill_categories:
            category = SkillCategory.objects.create(**category_data)
            self.stdout.write(self.style.SUCCESS(f'成功创建技能分类: {category}'))

        self.stdout.write(self.style.SUCCESS('所有数据初始化完成！')) 