from rest_framework import permissions


class IsMessageOrReplyOwner(permissions.BasePermission):
    """
    自定义权限类：验证用户是否是留言或回复的作者
    - 超级用户可以删除任何留言或回复
    - 普通用户只能删除自己的留言或回复
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # 超级用户可以访问所有对象
        if request.user.is_superuser:
            return True
        
        # 检查是否是用户自己的数据
        return request.user.uid == obj.user.uid 