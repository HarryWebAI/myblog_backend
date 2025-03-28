from rest_framework import permissions

class IsSuperUser(permissions.BasePermission):
    """
    自定义权限类：验证用户是否登录且是超级用户
    """
    def has_permission(self, request, view):
        
        # 检查用户是否是超级用户
        return request.user.is_superuser

class IsSuperUserOrSelf(permissions.BasePermission):
    """
    自定义权限类：验证用户是否是超级用户或者是操作自己的数据
    - 超级用户可以访问所有内容
    - 普通用户只能查看和更新自己的信息
    """
    def has_permission(self, request, view):
        # 确保用户已登录
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # 超级用户可以访问所有对象
        if request.user.is_superuser:
            return True
        
        # 普通用户只能访问自己的对象
        return obj.uid == request.user.uid