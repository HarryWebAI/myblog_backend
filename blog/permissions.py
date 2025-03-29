from rest_framework import permissions

class IsSuperUserOrReadOnly(permissions.BasePermission):
    """
    自定义权限类:
    - 所有用户都可以查看
    - 只有超级用户可以编辑
    """
    def has_permission(self, request, view):
        # 允许所有用户查看
        if request.method in permissions.SAFE_METHODS:
            return True
        # 只有超级用户可以编辑
        return request.user and request.user.is_superuser 