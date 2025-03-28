from rest_framework import serializers
from .models import Welcome, Description


class DescriptionSerializer(serializers.ModelSerializer):
    """
    描述信息序列化器
    """
    class Meta:
        model = Description
        fields = ['id', 'content']
        read_only_fields = ['id']


class WelcomeSerializer(serializers.ModelSerializer):
    """
    欢迎信息序列化器，包含关联的描述信息
    """
    # 使用关联名称获取所有关联的描述信息
    descriptions = DescriptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Welcome
        fields = ['id', 'title', 'buttonText', 'descriptions']
        read_only_fields = ['id']

class UpdateWelcomeSerializer(serializers.Serializer):
    title = serializers.CharField(
        max_length=10,
        required=False,
        error_messages={
            'max_length': '标题长度不能超过10个字符'
        }
    )
    buttonText = serializers.CharField(
        max_length=10,
        required=False,
        error_messages={
            'max_length': '按钮文本长度不能超过10个字符'
        }
    )
    descriptions = DescriptionSerializer(
        many=True,
        required=False,
        error_messages={
            'required': '描述信息不能为空'
        }
    )

