from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import WorkExperience, Education, Project, SkillCategory
from .serializers import (
    WorkExperienceSerializer,
    EducationSerializer,
    ProjectSerializer,
    SkillCategorySerializer,
    UpdateAboutMeSerializer
)
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db import transaction
import logging
from bloguser.permissons import IsSuperUser
from django_redis import get_redis_connection

# 创建日志记录器
logger = logging.getLogger(__name__)

# 缓存时间: 12小时
ABOUTME_CACHE_TTL = 60 * 60 * 12  # 12小时, 以秒为单位
ABOUTME_CACHE_KEY = 'harry_web_ai_aboutme'

class AboutMeView(APIView):
    """
    关于我API
    GET: 获取所有aboutme数据, 包含work, education, projects, skills
    """
    
    @method_decorator(
        cache_page(ABOUTME_CACHE_TTL, key_prefix=ABOUTME_CACHE_KEY)
    )
    def get(self, request):
        """获取所有aboutme数据(使用Redis缓存, 缓存时间12小时)"""
        try:
            logger.info("获取aboutme数据(如果命中缓存, 此日志在缓存期内只会出现一次)")
            # 获取并序列化所有数据
            work_experiences = WorkExperienceSerializer(WorkExperience.objects.all(), many=True).data
            educations = EducationSerializer(Education.objects.all(), many=True).data
            projects = ProjectSerializer(Project.objects.all(), many=True).data
            skill_categories = SkillCategorySerializer(SkillCategory.objects.all(), many=True).data

            return Response({
                'code': 200,
                'data': {
                    'work': work_experiences,
                    'education': educations,
                    'projects': projects,
                    'skills': skill_categories
                }
            })
        except Exception as e:
            logger.error(f"获取aboutme数据出错: {str(e)}")
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateAboutMeView(APIView):
    """
    更新aboutme数据(仅限管理员)
    """
    permission_classes = [IsSuperUser]

    def put(self, request):
        serializer = UpdateAboutMeSerializer(data=request.data)

        # 序列化器验证
        if serializer.is_valid():
            try:
                # 开启数据库事务
                with transaction.atomic():
                    # 清空现有数据
                    WorkExperience.objects.all().delete()
                    Education.objects.all().delete()
                    Project.objects.all().delete()
                    SkillCategory.objects.all().delete()

                    # 创建新数据
                    for work_data in serializer.validated_data['work']:
                        WorkExperience.objects.create(**work_data)

                    for education_data in serializer.validated_data['education']:
                        Education.objects.create(**education_data)

                    for project_data in serializer.validated_data['projects']:
                        Project.objects.create(**project_data)

                    for skill_data in serializer.validated_data['skills']:
                        SkillCategory.objects.create(**skill_data)

                # 提交数据库事务
                transaction.commit()

                # 清除缓存
                try:
                    redis = get_redis_connection("default")
                    pattern = f":1:views.decorators.cache.*{ABOUTME_CACHE_KEY}*"
                    for key in redis.scan_iter(pattern):
                        redis.delete(key)
                        logger.info(f"已删除缓存键: {key}")
                except Exception as e:
                    logger.error(f"清除缓存时出错: {str(e)}")

                return Response({
                    'code': 200,
                    'message': '更新成功'
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    'code': 500,
                    'message': f'服务器错误: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                'code': 400,
                'message': list(serializer.errors.values())[0][0]
            }, status=status.HTTP_400_BAD_REQUEST)
