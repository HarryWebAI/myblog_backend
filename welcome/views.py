from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Welcome, Description
from .serializers import WelcomeSerializer, UpdateWelcomeSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db import transaction
import logging
from bloguser.permissons import IsSuperUser
from django_redis import get_redis_connection


# 创建日志记录器
logger = logging.getLogger(__name__)

# 缓存时间: 12小时
WELCOME_CACHE_TTL = 60 * 60 * 12  # 12小时, 以秒为单位
WELCOME_CACHE_KEY = 'harry_web_ai_welcome'
class WelcomeView(APIView):
    """
    欢迎信息API
    GET: 获取唯一的welcome数据, 包含title, buttonText及相关的descriptions
    PUT: 更新welcome数据(仅限管理员)
    """
    
    @method_decorator(
        cache_page(WELCOME_CACHE_TTL, key_prefix=WELCOME_CACHE_KEY)
    )
    def get(self, request):
        """获取唯一的welcome数据(使用Redis缓存, 缓存时间12小时)"""
        # 获取第一条数据, 如果不存在则返回404
        try:
            logger.info("获取welcome数据(如果命中缓存, 此日志在缓存期内只会出现一次)")
            welcome = Welcome.objects.first()
            if not welcome:
                return Response({
                    'code': 404,
                    'message': '欢迎数据不存在'
                }, status=status.HTTP_404_NOT_FOUND)
                
            serializer = WelcomeSerializer(welcome)
            return Response({
                'code': 200,
                'data': serializer.data
            })
        except Exception as e:
            logger.error(f"获取welcome数据出错: {str(e)}")
            return Response({
                'code': 500,
                'message': f'服务器错误: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        """更新唯一的welcome数据(仅限管理员)"""
        # 验证是否为管理员
        if not request.user.is_superuser:
            return Response({
                'code': 403,
                'message': '只有管理员才能更新欢迎数据'
            }, status=status.HTTP_403_FORBIDDEN)
            
        # 获取第一条数据, 如果不存在则创建
        welcome = Welcome.objects.first()
        if not welcome:
            welcome = Welcome()
            
        serializer = WelcomeSerializer(welcome, data=request.data)
        if serializer.is_valid():
            serializer.save()
            # 更新成功后, 可以手动清除缓存, 但这里我们依赖TTL自动过期即可
            return Response({
                'code': 200,
                'message': '欢迎数据更新成功',
                'data': serializer.data
            })
        else:
            return Response({
                'code': 400,
                'message': list(serializer.errors.values())[0][0]
            }, status=status.HTTP_400_BAD_REQUEST)


class UpdateWelcomeView(APIView):
    """
    更新welcome数据(仅限管理员)
    """
    permission_classes = [IsSuperUser]

    def put(self, request):
        serializer = UpdateWelcomeSerializer(data=request.data)
        descriptions = []

        # 序列化器验证
        if serializer.is_valid():
            try:
                # 开启数据库事务
                with transaction.atomic():
                    # 更新welcome数据
                    welcome = Welcome.objects.first()
                    welcome.title = serializer.validated_data['title']
                    welcome.buttonText = serializer.validated_data['buttonText']
                    welcome.save()

                    # 删除descriptions数据
                    Description.objects.all().delete()

                    # 创建新的descriptions数据
                    for description in serializer.validated_data['descriptions']:
                        descriptions.append(Description(
                            content=description['content'],
                            welcome=welcome
                        ))

                    Description.objects.bulk_create(descriptions)

                # 提交数据库事务
                transaction.commit()

                # 清除缓存
                try:
                    redis = get_redis_connection("default")
                    pattern = f":1:views.decorators.cache.*{WELCOME_CACHE_KEY}*"
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
