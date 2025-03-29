from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsMessageOrReplyOwner
from .models import Message, Reply
from .serializers import MessageSerializer, ReplySerializer
from .paginations import MessagePagination

# Create your views here.

class MessageViewSet(viewsets.ModelViewSet):
    """
    留言视图集
    - list: 获取所有留言列表（公开访问）
    - create: 创建新留言（需要登录）
    - create_reply: 创建回复（需要登录）
    - destroy: 删除留言（仅留言作者或超级用户可删除）
    - delete_reply: 删除回复（仅回复作者或超级用户可删除）
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    pagination_class = MessagePagination

    def get_permissions(self):
        """
        根据不同的操作设置不同的权限
        """
        if self.action == 'list':
            # 获取列表公开访问
            permission_classes = [AllowAny]
        elif self.action in ['destroy', 'delete_reply']:
            # 删除操作需要是作者或超级用户
            permission_classes = [IsAuthenticated, IsMessageOrReplyOwner]
        else:
            # 其他操作需要登录
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """
        创建留言时自动设置用户
        """
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def create_reply(self, request, pk=None):
        """
        创建回复
        """
        message = self.get_object()
        serializer = ReplySerializer(data=request.data)
        
        if serializer.is_valid():
            # 设置回复的用户和关联的留言
            serializer.save(
                user=request.user,
                message=message
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='replies/(?P<reply_id>[^/.]+)')
    def delete_reply(self, request, pk=None, reply_id=None):
        """
        删除回复
        """
        try:
            # 直接从 Reply 模型中获取回复对象
            reply = Reply.objects.get(id=reply_id, message_id=pk)
            # 检查权限
            self.check_object_permissions(request, reply)
            # 删除回复
            reply.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Reply.DoesNotExist:
            return Response(
                {'detail': '回复不存在'}, 
                status=status.HTTP_404_NOT_FOUND
            )
