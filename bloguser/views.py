from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer, InitCodeSerializer, RegisterSerializer, AvatarUploadSerializer, ActiveUserSerializer, ResetPasswordSerializer
from .authentications import generate_jwt
import random
import redis
from django.core.mail import send_mail
from django.conf import settings
from .models import BlogUser
from rest_framework.viewsets import ModelViewSet
from .permissons import IsSuperUser, IsSuperUserOrSelf
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserModelSerializer, UserUpdateSerializer
from django.utils import timezone
from rest_framework.parsers import MultiPartParser
import os
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.viewsets import GenericViewSet
from urllib.parse import quote


# Redis连接配置
redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=1)  # 直接使用数据库1

class LoginView(APIView):
    """
    用户登录接口
    """
    
    def post(self, request):
        # 创建序列化器实例
        serializer = LoginSerializer(data=request.data)
        
        # 验证数据
        if serializer.is_valid():
            # 获取验证后的数据中的用户对象
            user = serializer.validated_data['user']
            user.last_login = timezone.now()
            user.save()
            
            # 生成JWT token
            token = generate_jwt(user)
            
            # 返回用户信息和token
            return Response({
                'code': 200,
                'message': '登录成功',
                'token': token,
                'user': {
                    'uid': user.uid,
                    'email': user.email,
                    'name': user.name,
                    'avatar': user.avatar,
                    'telephone': user.telephone,
                    'is_superuser': user.is_superuser,
                }
            }, status=status.HTTP_200_OK)
        else:
            # 获取错误信息
            error = list(serializer.errors.values())[0][0]
            return Response({
                'code': status.HTTP_400_BAD_REQUEST,
                'message': error,
            }, status=status.HTTP_400_BAD_REQUEST)
        
class InitCodeView(APIView):
    """
    初始化验证码接口
    """
    
    def post(self, request):
        # 创建序列化器实例
        serializer = InitCodeSerializer(data=request.data)

        # 验证数据
        if serializer.is_valid():
            email = serializer.validated_data['email']

            # 生成验证码
            code = random.randint(100000, 999999)

            # 保存验证码到redis中, 有效期为5分钟
            redis_key = f"email_code:{email}"
            try:
                redis_client.setex(redis_key, 300, str(code))  # 300秒 = 5分钟
            except redis.ConnectionError as e:
                print(f"Redis连接错误: {str(e)}")
                return Response({
                    'code': 500,
                    'message': 'Redis连接失败'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 发送验证码邮件
            subject = '欢迎注册 HarryWebAI 的博客!'
            message = f'您的验证码是：{code}, 有效期为5分钟! 请勿将验证码泄露给他人!'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]
            
            # 发送邮件
            try:
                send_mail(subject, message, from_email, recipient_list)
            except Exception as e:
                return Response({
                    'code': 500,
                    'message': '邮件发送失败'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 返回成功信息
            return Response({
                'code': 200,
                'message': '验证码发送成功'
            }, status=status.HTTP_200_OK)
        else:
            # 获取错误信息
            error = list(serializer.errors.values())[0][0]
            return Response({
                'code': 400,
                'message': error
            }, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(APIView):
    """
    用户注册接口
    """
    
    def post(self, request):
        # 创建序列化器实例
        serializer = RegisterSerializer(data=request.data)

        # 验证数据
        if serializer.is_valid():
            email = serializer.validated_data['email']
            name = serializer.validated_data['name']
            telephone = serializer.validated_data['telephone']

            # 创建用户
            try:
                BlogUser.objects.create_user(email=email, name=name, telephone=telephone)
            except Exception as e:
                return Response({
                    'code': 500,
                    'message': '数据写入失败'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                'code': 200,
                'message': '注册成功, 请先随便逛逛, 等待博主审核!'
            }, status=status.HTTP_200_OK)
        else:
            # 获取错误信息
            error = list(serializer.errors.values())[0][0]
            return Response({
                'code': 400,
                'message': error
            }, status=status.HTTP_400_BAD_REQUEST)

class UserModelViewSet(ListModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    """
    用户模型视图集
    - list: 获取所有用户列表（仅超级用户可访问）
    - update: 更新用户名称（仅用户自己和超级用户可更新）
    - destroy: 删除用户（仅用户自己和超级用户可删除，且不能删除超级用户）
    """
    queryset = BlogUser.objects.all()
    serializer_class = UserModelSerializer
    permission_classes = [IsAuthenticated, IsSuperUserOrSelf]

    def get_serializer_class(self):
        """
        根据不同的操作使用不同的序列化器
        """
        if self.action == 'update':
            return UserUpdateSerializer
        return UserModelSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def destroy(self, request, *args, **kwargs):
        """
        重写删除方法，添加超级用户保护
        """
        instance = self.get_object()
        
        # 检查是否是超级用户
        if instance.is_superuser:
            return Response({
                'code': 400,
                'message': '你连自己也删?'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        return super().destroy(request, *args, **kwargs)

class AvatarUploadView(APIView):
    """
    头像上传接口
    """
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]
    serializer_class = AvatarUploadSerializer

    def post(self, request):
        try:
            # 获取上传的文件
            avatar_file = request.FILES.get('avatar')
            if not avatar_file:
                return Response({
                    'code': 400,
                    'message': '请选择要上传的头像'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 生成文件名（使用时间戳和用户ID）
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            filename = f'avatar_{request.user.uid}_{timestamp}.jpg'
            
            # 确保目录存在
            avatar_dir = os.path.join(settings.MEDIA_ROOT, 'avatar')
            os.makedirs(avatar_dir, exist_ok=True)
            
            # 保存文件
            file_path = os.path.join(avatar_dir, filename)
            with open(file_path, 'wb') as f:
                for chunk in avatar_file.chunks():
                    f.write(chunk)
            
            # 更新用户头像路径
            request.user.avatar = f'/media/avatar/{filename}'
            print(request.user.avatar)
            request.user.save()
            
            # 返回头像URL
            return Response({
                'code': 200,
                'message': '头像上传成功',
                'url': f'/media/avatar/{filename}'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print("上传失败:", str(e))
            return Response({
                'code': 500,
                'message': f'头像上传失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AgreeUserView(APIView):
    """
    同意用户激活接口
    """
    permission_classes = [IsAuthenticated, IsSuperUser]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({
                'code': 400,
                'message': '请提供用户邮箱'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 生成6位随机数字
        random_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # 拼接邮箱和随机码
        combined_str = f"{email}{random_code}"
        
        # 简单加密（这里使用base64作为示例）
        import base64
        encrypted_str = base64.b64encode(combined_str.encode()).decode()
        
        # 使用 settings 中配置的前端地址
        frontend_url = settings.FRONTEND_URL
        active_url = f"{frontend_url}/active?activekey={encrypted_str}"
        
        # 发送邮件
        try:
            send_mail(
                subject='博客用户激活',
                message=f'请点击以下链接激活您的账号：{active_url}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
            
            # 将验证码存入Redis，设置30分钟过期
            redis_client.setex(f"active_{email}", 1800, random_code)
            
            return Response({
                'code': 200,
                'message': '激活邮件发送成功'
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'邮件发送失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ActiveUserView(APIView):
    """
    激活用户接口
    """
    permission_classes = [AllowAny]  # 允许未登录用户访问

    def post(self, request):
        # 创建序列化器实例
        serializer = ActiveUserSerializer(data=request.data)
        
        # 验证数据
        if serializer.is_valid():
            # 获取验证后的数据
            validated_data = serializer.validated_data
            user = validated_data['user']
            password = validated_data['password']
            
            # 设置密码并激活用户
            user.set_password(password)
            user.is_active = True
            user.save()
            
            # 删除Redis中的验证码
            redis_client.delete(f"active_{user.email}")
            
            return Response({
                'code': 200,
                'message': '用户激活成功',
                'user': {
                    'uid': user.uid,
                    'email': user.email,
                    'name': user.name,
                    'avatar': user.avatar,
                    'telephone': user.telephone,
                    'is_superuser': user.is_superuser,
                }
            }, status=status.HTTP_200_OK)
        else:
            # 获取错误信息
            error = list(serializer.errors.values())[0][0]
            return Response({
                'code': 400,
                'message': error
            }, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    """
    重置密码接口
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            password = serializer.validated_data['password']
            user.set_password(password)
            user.save()
            return Response({
                'code': 200,
                'message': '密码重置成功'
            }, status=status.HTTP_200_OK)
        else:
            # 获取错误信息
            error = list(serializer.errors.values())[0][0]
            return Response({
                'code': 400,
                'message': error
            }, status=status.HTTP_400_BAD_REQUEST)