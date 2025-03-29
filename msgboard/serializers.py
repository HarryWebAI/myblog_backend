from rest_framework import serializers
from .models import Message, Reply
from bloguser.serializers import UserModelSerializer


class ReplySerializer(serializers.ModelSerializer):
    """
    回复序列化器
    """
    user = UserModelSerializer(read_only=True)
    reply_to = serializers.SerializerMethodField()

    class Meta:
        model = Reply
        fields = ['id', 'user', 'time', 'content', 'parent_reply', 'reply_to']
        read_only_fields = ['id', 'time']

    def get_reply_to(self, obj):
        """
        获取回复对象的用户名
        """
        if obj.parent_reply:
            return obj.parent_reply.user.name
        return None


class MessageSerializer(serializers.ModelSerializer):
    """
    留言序列化器
    """
    user = UserModelSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'user', 'time', 'content', 'replies']
        read_only_fields = ['id', 'time']

    def get_replies(self, obj):
        """
        获取所有回复, 包括对留言的回复和对回复的回复
        """
        return ReplySerializer(obj.replies.all(), many=True).data
