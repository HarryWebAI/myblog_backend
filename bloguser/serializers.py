from rest_framework import serializers
from .models import BlogUser
from django.contrib.auth.hashers import check_password
from django.conf import settings
import redis
from django.contrib.auth import authenticate
from django.db.models import Q
import base64

# Redis连接配置
redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=1)


class LoginSerializer(serializers.Serializer):
    """
    登录表单后端验证序列化器
    """
    email = serializers.EmailField(
        error_messages={
            'required': '邮箱不能为空',
            'invalid': '请输入有效的邮箱地址'
        }
    )
    
    password = serializers.CharField(
        min_length=6,
        error_messages={
            'required': '密码不能为空',
            'min_length': '密码长度不能少于6位'
        }
    )

    def validate(self, attrs):
        """
        验证用户是否存在以及密码是否正确
        """
        email = attrs.get('email')
        password = attrs.get('password')
        
        # 验证用户是否存在
        try:
            user = BlogUser.objects.get(email=email)
        except BlogUser.DoesNotExist:
            raise serializers.ValidationError({'email': '该邮箱未注册'})
        
        # 判断用户是否激活
        if not user.is_active:
            raise serializers.ValidationError({'email': '该账号已被禁用'})

        #  验证密码是否正确
        if not check_password(password, user.password):
            raise serializers.ValidationError({'password': '密码错误'})
        
        # 将用户对象添加到验证后的数据中
        attrs['user'] = user

        return attrs
    
class InitCodeSerializer(serializers.Serializer):
    """
    初始化验证码序列化器
    """
    email = serializers.EmailField(
        error_messages={
            'required': '邮箱不能为空',
            'invalid': '请输入有效的邮箱地址'
        }
    )

class RegisterSerializer(serializers.Serializer):
    """
    用户注册序列化器
    """
    email = serializers.EmailField(
        error_messages={
            'required': '邮箱不能为空',
            'invalid': '请输入有效的邮箱地址'
        }
    )

    code = serializers.CharField(
        min_length=6,
        max_length=6,
        error_messages={
            'required': '验证码不能为空',
            'min_length': '验证码长度不能少于6位'
        }
    )

    name = serializers.CharField(
        min_length=2,
        max_length=10,
        error_messages={
            'required': '姓名不能为空',
            'min_length': '姓名长度不能少于2位',
            'max_length': '姓名长度不能超过10位'
        }
    )

    telephone = serializers.CharField(
        min_length=11,
        max_length=11,
        error_messages={
            'required': '手机号不能为空',
            'min_length': '请输入正确的手机号',
            'max_length': '请输入正确的手机号'
        }
    )

    def validate(self, attrs):
        # 验证验证码
        email = attrs.get('email')
        code = attrs.get('code')
        redis_key = f"email_code:{email}"
        stored_code = redis_client.get(redis_key)
        print(f"输入的验证码: {code}, 存储的验证码: {stored_code}")  # 添加调试信息
        if not stored_code or stored_code.decode() != str(code):
            raise serializers.ValidationError({'code': '验证码错误'})
        
        # 验证邮箱和手机号是否已注册
        telephone = attrs.get('telephone')
        # 使用Q对象优化查询
        existing_user = BlogUser.objects.filter(Q(email=email) | Q(telephone=telephone)).first()
        if existing_user:
            if existing_user.email == email:
                raise serializers.ValidationError({'email': '电子邮箱已被注册'})
            if existing_user.telephone == telephone:
                raise serializers.ValidationError({'telephone': '手机号码已被注册'})
        
        return attrs
    
class UserModelSerializer(serializers.ModelSerializer):
    """
    用户模型序列化器 - 用于读取用户信息
    """
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = BlogUser
        exclude = ['password', 'is_superuser', 'is_staff', 'avatar', 'groups', 'user_permissions']  # 排除密码字段
        read_only_fields = ['uid', 'email', 'is_superuser', 'is_staff', 'last_login']

    def get_avatar_url(self, obj):
        """
        获取头像的完整 URL
        """
        request = self.context.get('request')
        if request and obj.avatar:
            return request.build_absolute_uri(obj.avatar)
        return obj.avatar

class UserUpdateSerializer(serializers.Serializer):
    """
    用户更新序列化器 - 专用于更新用户信息
    只允许用户修改自己的名字
    """
    name = serializers.CharField(
        min_length=2,
        max_length=10,
        error_messages={
            'required': '姓名不能为空',
            'min_length': '姓名长度不能少于2位',
            'max_length': '姓名长度不能超过10位'
        }
    )
    
    def update(self, instance, validated_data):
        """
        更新用户实例的name字段
        """
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance

class AvatarUploadSerializer(serializers.Serializer):
    """
    头像上传序列化器
    """
    avatar = serializers.FileField(
        required=True,
        error_messages={
            'required': '请选择要上传的头像',
            'invalid': '请上传有效的文件'
        }
    )

    def validate_avatar(self, value):
        """
        验证头像文件
        """
        # 检查文件大小（限制为5MB）
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError('头像大小不能超过5MB')
        
        # 检查文件类型
        content_type = value.content_type.lower()
        if content_type != 'image/jpeg':
            raise serializers.ValidationError('头像必须是jpg格式')
        
        return value

class ActiveUserSerializer(serializers.Serializer):
    """
    用户激活序列化器
    """
    activekey = serializers.CharField(
        required=True,
        error_messages={
            'required': '激活链接不能为空'
        }
    )
    
    password = serializers.CharField(
        min_length=6,
        required=True,
        error_messages={
            'required': '密码不能为空',
            'min_length': '密码长度不能少于6位'
        }
    )
    
    confirm_password = serializers.CharField(
        required=True,
        error_messages={
            'required': '确认密码不能为空'
        }
    )

    def validate(self, attrs):
        # 验证两次密码输入是否一致
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        
        if password != confirm_password:
            raise serializers.ValidationError({'confirm_password': '两次输入的密码不一致'})
        
        # 验证激活链接
        activekey = attrs.get('activekey')
        try:
            # base64解码
            decoded_str = base64.b64decode(activekey.encode()).decode()
            
            # 拆分字符串，后6位为验证码，前面为用户邮箱
            email = decoded_str[:-6]
            verification_code = decoded_str[-6:]
            print(f"解码后的字符串: {decoded_str}, 邮箱: {email}, 验证码: {verification_code}")
            
            # 从Redis获取存储的验证码
            stored_code = redis_client.get(f"active_{email}")
            if not stored_code:
                raise serializers.ValidationError({'activekey': '激活链接已过期'})
            
            # 验证码比对 - 比对解密后的后6位验证码
            if stored_code.decode() != verification_code:
                raise serializers.ValidationError({'activekey': '验证码错误'})
            
            # 查找用户
            try:
                user = BlogUser.objects.get(email=email)
                if user.is_active:
                    raise serializers.ValidationError({'activekey': '该用户已经激活'})
            except BlogUser.DoesNotExist:
                raise serializers.ValidationError({'activekey': '用户不存在'})
            
            # 只返回必要的数据
            return {
                'user': user,
                'password': password
            }
            
        except base64.binascii.Error:
            raise serializers.ValidationError({'activekey': '无效的激活链接'})
        except Exception as e:
            raise serializers.ValidationError({'activekey': str(e)})

class ResetPasswordSerializer(serializers.Serializer):
    """
    重置密码序列化器
    """
    uid = serializers.CharField(
        required=True,
        error_messages={
            'required': '未传入有效用户ID'
        }
    )
    
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': '未传入有效邮箱'
        }
    )

    old_password = serializers.CharField(
        min_length=6,
        required=True,
        error_messages={
            'required': '未传入旧密码',
            'min_length': '旧密码长度不能少于6位'
        }
    )

    password = serializers.CharField(
        min_length=6,
        required=True,
        error_messages={
            'required': '密码不能为空',
            'min_length': '密码长度不能少于6位'
        }
    )

    confirm_password = serializers.CharField(
        required=True,
        error_messages={
            'required': '确认密码不能为空'
        }
    )

    def validate(self, attrs):
        # 验证两次密码是否正确
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        old_password = attrs.get('old_password')
        email = attrs.get('email')
        uid = attrs.get('uid')

        # 验证两次密码是否一致
        if password != confirm_password:
            raise serializers.ValidationError({'confirm_password': '两次输入的密码不一致'})
        
        # 验证邮箱和Uid
        try:
            user = BlogUser.objects.get(email=email, uid=uid)
        except BlogUser.DoesNotExist:
            raise serializers.ValidationError({'email': '邮箱或用户ID错误'})
        
        # 验证旧密码是否正确
        if not check_password(old_password, user.password):
            raise serializers.ValidationError({'old_password': '旧密码错误'})
        
        # 验证用户是否激活
        if not user.is_active:
            raise serializers.ValidationError({'email': '该用户未激活'})
        
        attrs['user'] = user

        return attrs
    