from rest_framework.pagination import PageNumberPagination


class MessagePagination(PageNumberPagination):
    """
    留言分页器
    """
    page_size = 3
