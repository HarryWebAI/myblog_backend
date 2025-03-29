from django.core.management.base import BaseCommand
from blog.models import Category, Tag, Blog
from django.utils import timezone
import random
import uuid

class Command(BaseCommand):
    help = '初始化博客数据'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化博客数据...')
        
        # 第一步: 创建分类
        self.create_categories()
        
        # 第二步: 创建标签
        self.create_tags()
        
        # 第三步: 创建博客
        self.create_blogs()
        
        self.stdout.write(self.style.SUCCESS('数据初始化完成!'))
    
    def create_categories(self):
        """创建分类"""
        self.stdout.write('开始创建分类...')
        
        categories = [
            {'name': '编程语言', 'slug': 'programming-languages', 'description': '各种编程语言相关文章'},
            {'name': '前端开发', 'slug': 'frontend-dev', 'description': '前端技术、框架和工具'},
            {'name': '后端开发', 'slug': 'backend-dev', 'description': '后端技术、框架和架构'},
            {'name': '数据库', 'slug': 'database', 'description': '数据库技术和优化'},
            {'name': '人工智能', 'slug': 'ai', 'description': 'AI、机器学习和深度学习'},
            {'name': '运维部署', 'slug': 'devops', 'description': '服务器运维和部署'},
            {'name': '区块链', 'slug': 'blockchain', 'description': '区块链和加密货币技术'},
            {'name': '网络安全', 'slug': 'security', 'description': '网络安全和渗透测试'},
            {'name': '算法与数据结构', 'slug': 'algorithm', 'description': '算法设计和数据结构'},
            {'name': '工具资源', 'slug': 'tools', 'description': '开发工具和资源分享'},
            {'name': '程序人生', 'slug': 'programmer-life', 'description': '技术人生活感悟和经验分享'},
            {'name': '项目实战', 'slug': 'projects', 'description': '实际项目经验和案例分析'},
        ]
        
        # 先清空现有分类
        Category.objects.all().delete()
        self.stdout.write('已清空现有分类数据')
        
        # 创建新分类
        for cat_data in categories:
            category = Category.objects.create(
                name=cat_data['name'],
                slug=cat_data['slug'],
                description=cat_data['description']
            )
            self.stdout.write(f'创建分类: {category.name}')
        
        self.stdout.write(self.style.SUCCESS(f'成功创建 {len(categories)} 个分类'))
    
    def create_tags(self):
        """创建标签"""
        self.stdout.write('开始创建标签...')
        
        tag_names = [
            # 编程语言
            'Python', 'JavaScript', 'Java', 'Go', 'C++', 'Rust', 'PHP', 'Ruby', 'Swift',
            # 前端
            'React', 'Vue', 'Angular', 'TypeScript', 'Node.js', 'CSS', 'HTML5', 'Webpack',
            # 后端
            'Django', 'Flask', 'Spring Boot', 'Express', 'Laravel', 'FastAPI', 'GraphQL',
            # 数据库
            'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'ElasticSearch', 'SQLite', 'Oracle',
            # 运维
            'Docker', 'Kubernetes', 'CI/CD', 'DevOps', 'Linux', 'Nginx', 'AWS', 'Azure',
            # 工具
            'Git', 'GitHub', 'GitLab', 'SVN'
        ]
        
        # 先清空现有标签
        Tag.objects.all().delete()
        self.stdout.write('已清空现有标签数据')
        
        # 创建新标签
        for tag_name in tag_names:
            # 处理slug
            tag_slug = f"{tag_name.lower().replace(' ', '-')}-{uuid.uuid4().hex[:4]}"
            tag = Tag.objects.create(
                name=tag_name,
                slug=tag_slug
            )
            self.stdout.write(f'创建标签: {tag.name}')
        
        self.stdout.write(self.style.SUCCESS(f'成功创建 {len(tag_names)} 个标签'))
    
    def create_blogs(self):
        """创建博客文章"""
        self.stdout.write('开始创建博客文章...')
        
        blog_data = [
            {
                'title': 'Python异步编程详解',
                'content': '异步编程是现代Python开发中不可或缺的一部分，本文将介绍异步编程的基础概念，包括协程、事件循环以及asyncio库的使用...',
                'category_slug': 'programming-languages'
            },
            {
                'title': 'React Hooks最佳实践与性能优化',
                'content': 'React Hooks改变了我们编写React组件的方式，本文将分享一些使用Hooks的最佳实践，以及如何避免一些常见的性能陷阱...',
                'category_slug': 'frontend-dev'
            },
            {
                'title': 'Docker容器化应用的完整部署流程',
                'content': 'Docker的出现极大地简化了应用程序的部署过程，本文将分享一个完整的Docker容器化部署流程，从Dockerfile编写到多容器编排...',
                'category_slug': 'devops'
            },
            {
                'title': 'GraphQL vs RESTful API比较',
                'content': 'GraphQL和RESTful API是两种主流的API设计方案，本文将对比它们的优缺点，并提供选择建议...',
                'category_slug': 'backend-dev'
            },
            {
                'title': '深入浅出微服务架构',
                'content': '微服务架构已经成为现代应用开发的主流，本文将介绍如何从单体应用逐步迁移到微服务架构，以及过程中的挑战与解决方案...',
                'category_slug': 'backend-dev'
            },
            {
                'title': 'Redis高级特性与分布式锁实现',
                'content': 'Redis不仅仅是一个缓存系统，还提供了丰富的高级特性。本文将深入探讨Redis的高级用法，特别是分布式锁的实现原理...',
                'category_slug': 'database'
            },
            {
                'title': 'TypeScript高级类型系统详解',
                'content': 'TypeScript的类型系统非常强大，本文将带你探索高级类型特性，如泛型、条件类型、映射类型和类型推断...',
                'category_slug': 'programming-languages'
            },
            {
                'title': 'Kubernetes集群管理与自动扩缩容',
                'content': 'Kubernetes已经成为容器编排的标准，本文将介绍K8s集群的管理技巧，以及如何设计高效的自动扩缩容策略...',
                'category_slug': 'devops'
            },
            {
                'title': 'Vue3组合式API源码分析',
                'content': 'Vue3的组合式API是一个革命性的变化，本文将深入分析它的实现原理，以及其背后的响应式系统设计...',
                'category_slug': 'frontend-dev'
            },
            {
                'title': 'MySQL索引优化与查询性能调优',
                'content': 'MySQL性能优化是后端开发中的重要一环，本文将分享一些索引设计和查询优化的实用技巧...',
                'category_slug': 'database'
            },
            {
                'title': '前端工程化实践:从Webpack到Vite',
                'content': '前端工程化是现代前端开发的重要组成部分，本文将对比Webpack和Vite，讨论构建工具的演进...',
                'category_slug': 'frontend-dev'
            },
            {
                'title': 'Linux服务器性能监控与问题排查',
                'content': 'Linux服务器维护是一项基本技能，本文将介绍如何监控服务器性能，以及排查常见问题的方法...',
                'category_slug': 'devops'
            },
            {
                'title': '机器学习模型部署与生产环境实践',
                'content': '将机器学习模型部署到生产环境是一个复杂的工程问题，本文将分享一些最佳实践和常见陷阱...',
                'category_slug': 'ai'
            },
            {
                'title': 'OAuth2.0认证流程与安全实现',
                'content': 'OAuth2.0是现代认证的标准协议，本文将详细解析其认证流程，以及如何避免常见的安全漏洞...',
                'category_slug': 'security'
            },
            {
                'title': 'Git工作流与团队协作规范',
                'content': 'Git是现代开发中最重要的工具之一，本文将介绍一些高效的Git工作流，以及团队协作的最佳实践...',
                'category_slug': 'tools'
            },
            {
                'title': '前端安全:XSS与CSRF防御策略',
                'content': '前端安全是Web应用开发中不可忽视的一环，本文将介绍如何防御XSS和CSRF攻击...',
                'category_slug': 'security'
            },
            {
                'title': 'Java并发编程与线程池优化',
                'content': 'Java并发编程是后端开发的核心技能，本文将深入讨论线程池的优化和并发模式的选择...',
                'category_slug': 'programming-languages'
            },
            {
                'title': 'ElasticSearch聚合查询与数据分析',
                'content': 'ElasticSearch不仅是搜索引擎，还是强大的分析工具，本文将介绍如何使用其聚合功能进行数据分析...',
                'category_slug': 'database'
            },
            {
                'title': 'HTTP/3与QUIC协议详解',
                'content': 'HTTP/3是下一代HTTP协议，基于QUIC传输协议，本文将详细介绍其工作原理和优势...',
                'category_slug': 'backend-dev'
            },
            {
                'title': '区块链智能合约开发入门',
                'content': '区块链技术正在改变多个行业，本文将介绍智能合约的基本概念和开发方法，以及一些实际案例...',
                'category_slug': 'blockchain'
            }
        ]
        
        # 先清空现有博客
        Blog.objects.all().delete()
        self.stdout.write('已清空现有博客数据')
        
        # 获取所有分类和标签
        categories = {category.slug: category for category in Category.objects.all()}
        tags = list(Tag.objects.all())
        
        if not categories:
            self.stdout.write(self.style.ERROR('没有找到分类，请先创建分类!'))
            return
        
        if not tags:
            self.stdout.write(self.style.ERROR('没有找到标签，请先创建标签!'))
            return
        
        # 创建博客
        for blog_info in blog_data:
            # 获取对应分类
            category = categories.get(blog_info['category_slug'])
            if not category:
                self.stdout.write(self.style.WARNING(f"分类 {blog_info['category_slug']} 不存在，跳过创建博客 {blog_info['title']}"))
                continue
                
            # 生成唯一slug
            blog_slug = f"{blog_info['title'].lower().replace(' ', '-').replace(':', '-')}-{uuid.uuid4().hex[:6]}"
            
            # 创建博客
            blog = Blog.objects.create(
                title=blog_info['title'],
                content=blog_info['content'],
                summary=blog_info['content'][:100] + '...',
                category=category,
                status=random.choice(['published', 'published', 'published', 'draft']),  # 75%概率已发布
                published_at=timezone.now() - timezone.timedelta(days=random.randint(1, 100)),
                view_count=random.randint(100, 5000),
                like_count=random.randint(10, 500),
                comment_count=random.randint(0, 100),
                is_original=random.choice([True, True, True, False]),  # 75%概率原创
                is_top=random.choice([True, False, False, False, False]),  # 20%概率置顶
                slug=blog_slug
            )
            
            # 随机添加3-7个标签
            blog.tags.set(random.sample(tags, random.randint(3, min(7, len(tags)))))
            
            self.stdout.write(f'创建博客: {blog.title}')
        
        self.stdout.write(self.style.SUCCESS(f'成功创建 {len(blog_data)} 篇博客文章')) 